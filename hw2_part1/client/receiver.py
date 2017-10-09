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
        while receiving:

            # receive ack with data
            msg = self.get_message()

            # Unpack the object
            # m = pickle.loads(msg)

            # Verify the checksum
            if m.validate_checksum()

            # Acknowledge packet and send expected sequence number


            # Send the get command to the server


            # Get the bytes that we will be receiving
            # modified_message = self.get_message()
            # f_list = pickle.loads(modified_message)
            # print(f_list)


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
    script_name = argv[0]  # Snag the first argument (The script name)
    filename = "unknown"
    port_to_use = DEFAULT_PORT
    server_to_use = DEFAULT_SERVER
    error_packet_percent = 0

    # Make sure we have exactly
    if len(argv) != 3:
        sys.stderr.write("ERROR: Invalid number of arguments\n\n")

        sys.exit(2)
    else:
        try:
            opts, args = getopt.getopt(argv, "hf:a:p:e:", ["help", "file=", "address=", "port=", "error="])
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
                port_to_use = arg
            elif opt in ("-e", "--error"):
                error_packet_percent = arg


    # Create instance of client class, open socket, and send message
    print("Connecting to " + server_to_use + ":" + str(port_to_use) + " and requesting file: " + filename)
    print("Creating packet errors " + str(error_packet_percent) + "% of the time")
    server = FTPClient(port_to_use, server_to_use)
    server.open_socket()
    server.command_get(filename)


# Start the client
if __name__ == "__main__":
    main(sys.argv)
