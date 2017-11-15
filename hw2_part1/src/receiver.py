from socket import *
import sys                  # Used to get ARGV (Argument values)
import getopt               # Friendly command line options
import message              # Python specific format to import custom module
import pickle               # need this for serializing objects

import time
import errno

# Global settings
DEFAULT_PORT = 5000
DEFAULT_SERVER = "localhost"
CONNECTION_TIMEOUT = 10  # seconds
RECEIVE_BUFFER = 1460  # bytes
SEND_BUFFER = 1460  # bytes
WINDOW_SIZE = 5
DEBUG = True  # Set to true for more print messages


class FTPClient:
    def __init__(self, server_port=DEFAULT_PORT, server_name=DEFAULT_SERVER):
        self.server_port = server_port
        self.server_name = server_name
        self.client_socket = None
        self.file = None
        self.filename = ""

    def open_socket(self):
        # Open a socket
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.client_socket.bind(('', self.server_port))
        print("INFO: Connection Opened with server, waiting to start...")

    def open_file_to_write(self, filename):
        self.filename = filename
        self.file = open(filename, 'wb')
        print("INFO: Opened file" + filename + " for output.")

    def send_message(self, msg):
        m = pickle.dumps(msg)
        self.client_socket.sendto(m, (self.server_name, self.server_port))

    def get_message(self):
        # Receive a response from the Server and print it
        self.client_socket.settimeout(CONNECTION_TIMEOUT)
        try:
            msg, address = self.client_socket.recvfrom(RECEIVE_BUFFER)
            self.server_name = address[0]
            self.server_port = address[1]
        except IOError as e:
            if e.errno == errno.EWOULDBLOCK:
                print("Error: Client timed out, closing connection")
                return False
            else:
                print("Error: " + str(e))
                return False

        return pickle.loads(msg)  # Unpack the object

    def command_get(self, filename):
        receiving = True
        ack = message.Message("ack", 0, "".encode())
        packets = []
        next_seq = 1
        sender_done = False

        while receiving:
            # Remove packets from the queue up to next_seq, since next_seq is always in-order
            self.__dequeue(packets, next_seq)

            # receive data packet and unpack it
            m = self.get_message()

            # Check if getting the message failed
            if not m:
                break

            self.__debug_print_packet(m, next_seq)

            # Verify the checksum
            if m.is_valid():
                print("Debug: Valid") if DEBUG else None

                if m.sequence_number >= next_seq:
                    # Make sure we have room in the window
                    if len(packets) <= WINDOW_SIZE:

                        # If this is the last packet, make sure we know that the sender is done
                        if m.msg_type == "end":
                            sender_done = True

                        # If sender is done and we got the last expected packet, lets end this.
                        if sender_done and next_seq == m.sequence_number:
                            receiving = False

                        # Ignore acks
                        if m.msg_type != "ack":
                            # Add packet info to acknowledged packets (seq_num, next_seq, received)
                            packets.append(m)

                            # Update expected next sequence number
                            if next_seq == m.sequence_number:
                                next_seq = m.sequence_number + len(m.data)

                            # Acknowledge packet and send expected sequence number
                            ack.sequence_number = next_seq
                            ack.update_checksum()
                            self.send_message(ack)
                            print("Debug: Sending Ack " + str(next_seq)) if DEBUG else None
                        else:
                            print("Error: Server sent ack - Segment dropped")
                    else:
                        print("Error: Duplicate packet - Segment dropped")
                else:
                    print("Error: Buffer full - Segment dropped")
            else:
                print("Error: Expected packet # CRC Error – Segment dropped")

        # Assume that if the process is over, we are done with the file
        self.file.close()
        print("INFO: File received, exiting.")

    def __debug_print_packet(self, msg, next_seq):
        print("Debug: " + str(msg.sequence_number) + " " + msg.msg_type + " " + str(next_seq)) if DEBUG else None

    def __dequeue(self, msg_window, next_seq):
        i = len(msg_window) - 1
        while i >= 0:
            msg = msg_window[i]
            if msg.sequence_number < next_seq:
                print("Debug: Writing data") if DEBUG else None
                data_written = self.__write_to_file(msg)

                # If we were successful, delete the packet
                if data_written:
                    print("Debug: Deleting from Window") if DEBUG else None
                    del msg_window[i]
            i = i - 1

    def __write_to_file(self, msg):
        data = msg.data
        try:
            self.file.write(data)
        except IOError:
            print("Error: Could not write to file")
            return False
        except:
            print("Error: ", sys.exc_info()[0])
            return False

        return True

    def __del__(self):
        # Clean up
        print("INFO: Closing the socket")
        self.client_socket.close()


def print_help(script_name):
    print("Usage:   " + script_name + " -p <port> [-f <filename>]")
    print("")
    print(" -f, --file")
    print("    The filename to save the file as")
    print(" -p, --port")
    print("    The port number to connect to")
    print("Example: " + script_name + " -p 5000")


def main(argv):
    script_name = argv[0]  # Snag the first argument (The script name)
    filename = "downloaded"
    port_to_use = DEFAULT_PORT
    server_to_use = DEFAULT_SERVER

    try:
        opts, args = getopt.getopt(argv[1:], "hf:p:", ["help", "file=", "port="])
    except getopt.GetoptError:
        print_help(script_name)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help(script_name)
            sys.exit()
        elif opt in ("-f", "--file"):
            filename = arg
        elif opt in ("-p", "--port"):
            port_to_use = int(arg)


    # Create instance of client class, open socket, and send message
    print("INFO: Opening port: " + str(port_to_use))
    server = FTPClient(port_to_use, server_to_use)
    server.open_socket()
    server.open_file_to_write(filename)

    begin_time = time.time()
    server.command_get(filename)
    end_time = time.time()

    total_seconds = end_time - begin_time
    print("Total time taken: " + str(total_seconds))

# Start the client
if __name__ == "__main__":
    main(sys.argv)
