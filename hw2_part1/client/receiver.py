from socket import *
import sys                  # Used to get ARGV (Argument values)
import getopt               # Friendly command line options
from mylib import message   # Python specific format to import custom module
import pickle               # need this for serializing objects

# Global settings
DEFAULT_PORT = 5000
DEFAULT_SERVER = "localhost"
CONNECTION_TIMEOUT = 10  # seconds
RECEIVE_BUFFER = 1024  # bytes
SEND_BUFFER = 1024  # bytes

PACKET_SEQ_NUM_POS = 0
PACKET_EXP_SEQ_NUM_POS = 1
PACKET_RECV_POS = 2


class FTPClient:
    def __init__(self, server_port=DEFAULT_PORT, server_name=DEFAULT_SERVER):
        self.server_port = server_port
        self.server_name = server_name
        self.client_socket = None

    def open_socket(self):
        # Open a socket
        self.client_socket = socket(AF_INET, SOCK_DGRAM)
        self.client_socket.bind(('', self.server_port))
        print("Connection Opened with server, waiting to start...")

    def send_message(self, msg):
        self.client_socket.sendto(msg.encode(), (self.server_name, self.server_port))

    def get_message(self):
        # Receive a response from the Server and print it
        modified_message, address = self.client_socket.recvfrom(RECEIVE_BUFFER)
        return modified_message

    def command_get(self, filename):
        receiving = True
        m = message.Message("Start", 123, "My Message Data")
        ack = message.Message("ack", 0, "")
        packets = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]

        while receiving:

            # receive ack with data
            msg = self.get_message()

            # Unpack the object
            m = pickle.loads(msg)

            # Verify the checksum
            if m.is_valid():
                # Acknowledge packet and send expected sequence number
                ack.sequence_number = self.__get_expected_sequence(packets)
                self.send_message(ack)
            else:
                print("Error: Expected packet # CRC Error – Segment dropped")

    def __get_expected_sequence(self, packets):
        n = packets[0][PACKET_EXP_SEQ_NUM_POS]  # Set equal to the first packet

        # Loop over the packets, looking for the first that has not been received
        for p in packets:
            if p[PACKET_RECV_POS] == 0:
                n = p[PACKET_EXP_SEQ_NUM_POS]

        return n

    def __recv_file(self, filename, size):
        try:
            file = open(filename, 'wb')
            data = " - "
            received_data = 0
            while data:
                data, address = self.client_socket.recvfrom(RECEIVE_BUFFER)
                file.write(data)
                received_data = received_data + len(data)
                if received_data >= size:
                    print("File " + filename + " done downloading")
                    file.close()
                    break

        except IOError:
            print("Could not read file: ", filename)

        except:
            print("Unexpected error: ", sys.exc_info()[0])

    def __del__(self):
        # Clean up
        print("Closing the socket")
        self.client_socket.close()


def print_help(script_name):
    print("Usage:   " + script_name + " -p <port>")
    print("")
    print(" -p, --port")
    print("    The port number to connect to")
    print("Example: " + script_name + " -p 5000")


def main(argv):
    script_name = argv[0]  # Snag the first argument (The script name)
    filename = "unknown"
    port_to_use = DEFAULT_PORT
    server_to_use = DEFAULT_SERVER
    error_packet_percent = 0

    try:
        opts, args = getopt.getopt(argv, "hp:", ["help", "port="])
    except getopt.GetoptError:
        print_help(script_name)
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print_help(script_name)
            sys.exit()
        elif opt in ("-p", "--port"):
            port_to_use = arg


    # Create instance of client class, open socket, and send message
    print("Opening port: " + str(port_to_use))
    server = FTPClient(port_to_use, server_to_use)
    server.open_socket()
    server.command_get(filename)


# Start the client
if __name__ == "__main__":
    main(sys.argv)
