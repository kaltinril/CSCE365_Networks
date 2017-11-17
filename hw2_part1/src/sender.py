from socket import *        # Used for sending and receiving information over sockets
import sys                  # Used to get ARGV (Argument values)
import getopt               # Friendly command line options
import message   # Python specific format to import custom module
import window
import pickle               # need this for serializing objects
import errno
import time
from threading import Timer
import random

# Global settings
DEFAULT_PORT = 5000
DEFAULT_SERVER = "localhost"
CONNECTION_TIMEOUT = 0.5  # seconds
RECEIVE_BUFFER = 1300  # bytes
SEND_BUFFER = 1300  # bytes
WINDOW_SIZE = 5
DEBUG = False  # Set to true for more printed information

class FTPServer:
    def __init__(self, filename, server_port=DEFAULT_PORT, server_name=DEFAULT_SERVER, error_percent=0):
        self.server_port = server_port
        self.server_name = server_name
        self.server_socket = None
        self.file_handle = None
        self.filename = filename
        self.error_percent = float(error_percent)
        self.window = window.Window()
        self.seq_num = 1
        self.send_complete = False
        self.thread_pool = {}

    def open_socket(self):
        # Open a socket
        self.server_socket = socket(AF_INET, SOCK_DGRAM)

        # Wait for input, and respond
        print("INFO: The server is ready to receive")

    def open_file(self, mode="rb"):
        self.file_handle = open(self.filename, mode)

    def send_message(self, msg):
        m = pickle.dumps(msg)
        self.server_socket.sendto(m, (self.server_name, self.server_port))
        t = Timer(0.5, self.__verify_acked, [msg])

        # Add the Timer to the thread pool
        self.thread_pool[msg.sequence_number] = t

        t.start()

    def get_message(self):
        # Receive a response from the Server and print it
        self.server_socket.settimeout(0)  # Non-blocking mode
        try:
            msg, address = self.server_socket.recvfrom(RECEIVE_BUFFER)
            self.server_name = address[0]
            self.server_port = address[1]
        except IOError as e:
            if e.errno == errno.EWOULDBLOCK or e.errno == errno.ETIMEDOUT or str(e) == "timed out":
                return False
            else:
                print("Error: " + str(e))
                raise e

        return pickle.loads(msg)  # Unpack the object

    def send_file(self):
        not_done = True

        # Loop until done
        while not_done:
            # send expired packets
            self.__send_expired_packets()

            # send new packets (If room in window)
            self.__send_new_packets()

            # Check for acks (Do not block)
            # Returns FALSE if their was no data
            msg = self.get_message()
            while msg:
                # Remove packets that were successfully ack'd
                self.window.ack_message(msg)

                # Cleanup threads for ack'd messages by canceling them
                self.__cleanup_threads(msg.sequence_number)

                msg = self.get_message()

            if self.send_complete and self.window.is_empty():
                print("INFO: File done sending.")
                not_done = False

    def __cleanup_threads(self, current_ack):
        # Get all threads in the pool that need to be canceled
        for seq in list(self.thread_pool.keys()):
            if seq < current_ack:
                # Cancel the thread and then delete it from the pool
                self.thread_pool[seq].cancel()
                del self.thread_pool[seq]

    def __send_expired_packets(self):
        for msg in self.window.buffer:
            # Indicates we did not get an ACK back in required timeframe
            if msg.timeout_exceeded():
                print("Error: ack wasn't received - resending packet")
                msg.update_checksum()  # Correct the checksum so that it can be re-sent
                self.send_message(msg)

    # Be dumb, don't check to see if the message was removed from the array
    # After the call ends the msg will go out of scope anyways so should be
    # cleaned up by garbage collection
    def __verify_acked(self, msg):
        msg.checksum = -1

    def __send_new_packets(self):
        if self.window.is_room():
            # read next sequence from file
            data = self.__read_from_file()

            # add data to message
            if self.seq_num == 1:
                msg = message.Message("start", self.seq_num, data)
                print("Debug: Sending start ") if DEBUG else None
            elif not data:
                # If we are past the end of the file send a complete message
                # Do this by changing the message type
                # and setting the data to nothing
                msg = message.Message("end", self.seq_num, "".encode())
                self.send_complete = True
            else:
                msg = message.Message("data", self.seq_num, data)

            self.seq_num = self.seq_num + len(data)  # We may have only read a few bytes because we are at end of file

            # Randomly change the checksum to send a "bad" packet
            if random.random() < (self.error_percent / 100):
                msg.checksum = 1

            # Add msg to window
            self.window.add_message(msg)

            # Send message
            print("Debug: " + msg.msg_type) if DEBUG else None
            self.send_message(msg)

    def __read_from_file(self):
        try:
            data = self.file_handle.read(SEND_BUFFER)
            return data
        except:
            self.__log_connection_data("Error: " + sys.exc_info()[0])
            return False

    # Private methods
    def __log_connection_data(self, string, address):
        print(str(address[0]) + ":" + str(address[1]) + " - " + string)


    def __del__(self):
        # Clean up
        print("INFO: Closing the socket")
        self.server_socket.close()

def print_help(script_name):
    print("Usage:   " + script_name + " -f <filename> -a <serverAddress> -p <port> -e <error%>")
    print("")
    print(" -f, --file")
    print("    The filename to send to request from the server")
    print(" -a, --address")
    print("    The IP or Hostname to connect to")
    print(" -p, --port")
    print("    The port number to connect to")
    print(" -e, --error")
    print("    The numeric value for the percent of packets to cause the packets to error")
    print("Example: " + script_name + " localhost 5000")

def main(argv):
    script_name = argv[0]  # Snag the first argument (The script name
    port_to_use = DEFAULT_PORT
    error_packet_percent = 0
    filename = ""
    server_to_use = DEFAULT_SERVER

    # Make sure we have exactly
    if len(argv) < 3:
        sys.stderr.write("ERROR: Invalid number of arguments\n\n")
        print_help(script_name)
        sys.exit(2)
    else:
        try:
            opts, remainder = getopt.getopt(argv[1:], "hf:a:p:e:", ["help", "file=", "address=", "port=", "error="])
        except getopt.GetoptError:
            print_help(script_name)
            sys.exit(2)

        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print_help(script_name)
                sys.exit()
            elif opt in ("-f", "--file"):
                filename = arg
            elif opt in ("-a", "--address"):
                server_to_use = arg
            elif opt in ("-p", "--port"):
                port_to_use = int(arg)
            elif opt in ("-e", "--error"):
                error_packet_percent = arg

    print(opts)

    if filename == "":
        sys.stderr.write("Error: Filename must be supplied!")
        print_help(script_name)
        sys.exit(2)

    server = FTPServer(filename, port_to_use, server_to_use, error_packet_percent)
    server.open_socket()
    server.open_file()
    server.send_file()


# Start the server
if __name__ == "__main__":
    main(sys.argv)
