from socket import *        # Used for sending and receiving information over sockets
import sys                  # Used to get ARGV (Argument values)
import getopt               # Friendly command line options
import message   # Python specific format to import custom module
import pickle               # need this for serializing objects
import errno
import time

# Global settings
DEFAULT_PORT = 5000
DEFAULT_SERVER = "localhost"
CONNECTION_TIMEOUT = 0.5  # seconds
RECEIVE_BUFFER = 1460  # bytes
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
        self.error_percent = error_percent

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

    def get_message(self):
        # Receive a response from the Server and print it
        self.server_socket.settimeout(CONNECTION_TIMEOUT)
        try:
            msg, address = self.server_socket.recvfrom(RECEIVE_BUFFER)
            self.server_name = address[0]
            self.server_port = address[1]
        except IOError as e:
            if e.errno == errno.EWOULDBLOCK:
                print("Error: Client timed out, closing connection")
                time.sleep(1)  # short delay, no tight loops
                return False
            else:
                print("Error: " + str(e))
                raise e

        return pickle.loads(msg)  # Unpack the object

    def send_file(self):
        not_done = True
        msg_type = "data"
        seq_num = 1
        segments = []

        # read from file
        data = self.__read_from_file()
        msg = message.Message("start", seq_num, data)
        self.send_message(msg)
        seq_num = seq_num + len(data)
        segments.append(msg)

        data = self.__read_from_file()
        if not data:
            msg_type = "end"
            data = ""

        while not_done:
            # add read data to message and to buffer
            msg = message.Message(msg_type, seq_num, data)
            seq_num = seq_num + len(data)
            segments.append(msg)

            # Send message
            print("Debug: " + msg.msg_type) if DEBUG else None
            self.send_message(msg)

            # check for acks
            self.server_socket.settimeout(CONNECTION_TIMEOUT)
            msg = self.get_message()

            # Validate checksum of ack, as long as it was successful
            if msg:
                if msg.is_valid():
                    print("Debug: valid") if DEBUG else None
                    if msg.msg_type == "ack":
                        print("Debug: Ack") if DEBUG else None
                        self.__dequeue(segments, msg.sequence_number)

                # if no more data change msg_type to end
                # read from file if buffer space available
                if len(segments) <= WINDOW_SIZE:
                    data = self.__read_from_file()
                    if not data:
                        msg_type = "end"
                        data = "".encode()
            else:
                print("Error: ack not received - resending packet")

            if msg_type == "end" and len(segments) == 0:
                print("INFO: File done sending.")
                break


    def __dequeue(self, segments, ackd_seq):
        i = len(segments) - 1
        while i >= 0:
            msg = segments[i]

            # Was this the packet that was ackd?
            if msg.sequence_number + len(msg.data) == ackd_seq:
                print("Debug: Deleting from Window") if DEBUG else None
                del segments[i]

            i = i - 1

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
