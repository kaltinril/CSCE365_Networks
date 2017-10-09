from socket import *        # Used for sending and receiving information over sockets
import shlex                # need this for it's split that keeps quoted filenames
import pickle               # need this for serializing objects
import os                   # Need this for reading from the file system
import os.path              # Used to read the file
import sys                  # Used to get ARGV (Argument values)
import getopt               # Friendly command line options
import message   # Python specific format to import custom module

# Global settings
DEFAULT_PORT = 5000
DEFAULT_SERVER = "localhost"
CONNECTION_TIMEOUT = 10  # seconds
RECEIVE_BUFFER = 1460  # bytes
SEND_BUFFER = 1460  # bytes
WINDOW_SIZE = 5

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
        print("The server is ready to receive")

    def open_file(self, mode="rb"):
        self.file_handle = open(self.filename, mode)

    def send_message(self, msg):
        m = pickle.dump(msg)
        self.client_socket.sendto(m, (self.server_name, self.server_port))

    def get_message(self):
        # Receive a response from the Server and print it
        msg, address = self.client_socket.recvfrom(RECEIVE_BUFFER)
        return pickle.loads(msg)  # Unpack the object

    def send_file(self):
        not_done = True
        msg_type = "data"
        seq_num = 1
        segments = []

        # read from file
        data = self.__read_from_file()
        self.send_message(message.Message("start", seq_num, data))
        seq_num = seq_num + data

        while not_done:
            # add read data to message and to buffer
            msg = message.Message(msg_type, seq_num, data)
            seq_num = seq_num + data

            # Send message
            self.send_message(msg)

            # check for acks
            self.get_message()

            # if no more data change msg_type to end
            # read from file if buffer space available
            if len(segments) <= WINDOW_SIZE:
                data = self.__read_from_file()
                if not data:
                    msg_type = "end"
                    data = ""

    def __read_from_file(self):
        try:
            data = self.file_handle.read(SEND_BUFFER)
            return data
        except:
            self.__log_connection_data("Error: " + sys.exc_info()[0])
            return False


    def listen(self):
        # Loop until the end of time, or a key press
        while True:
            try:
                msg, address = self.server_socket.recvfrom(RECEIVE_BUFFER)
                msg = msg.decode()
                print(msg)
                self.__check_command(msg, self.server_socket, address)
            except:
                if self.server_socket.fileno() != -1:
                    self.server_socket.close()
                return False

    # Private methods
    def __log_connection_data(self, string, address):
        print(str(address[0]) + ":" + str(address[1]) + " - " + string)


    def __send_file_details(self, connection, command_and_args, address):
        self.__log_connection_data("Get a file", address)
        if len(command_and_args) < 2:
            e_list = pickle.dumps("Error: No filename provided with get!")
            connection.sendto(e_list, address)
        else:
            filename = command_and_args[1]
            if os.path.exists(filename):
                try:
                    size = os.stat(filename).st_size
                    self.__log_connection_data("Sending file: " + filename, address)
                    e_list = pickle.dumps("sending " + filename + " size " + str(size))
                    connection.sendto(e_list, address)

                    self.__send_file(connection, filename, address)

                except FileNotFoundError:
                    # doesn't exist
                    self.__log_connection_data("File not found: " + filename, address)
                    e_list = pickle.dumps("Error: File not found! " + filename)
                    connection.sendto(e_list, address)
                except:
                    self.__log_connection_data("Unexpected error:" + sys.exc_info()[0], address)
                    e_list = pickle.dumps("Error: Unknown error with file! " + filename)
                    connection.sendto(e_list, address)
            else:
                self.__log_connection_data("File not found: " + filename, address)
                e_list = pickle.dumps("Error: File not found! " + filename)
                connection.sendto(e_list, address)

    def __send_file(self, connection, filename, address):
        try:
            file = open(filename, 'rb')
            data = file.read(SEND_BUFFER)
            while data:
                connection.sendto(data, address)
                data = file.read(SEND_BUFFER)
        except:
            self.__log_connection_data("Unexpected error:" + sys.exc_info()[0], address)
            connection.sendto("Error: Unknown error reading file or sending file " + filename, address)

    def __del__(self):
        # Clean up
        print("Closing the socket")
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
            print(opts)
            print(remainder)
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
