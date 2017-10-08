from socket import *        # Used for sending and receiving information over sockets
import shlex                # need this for it's split that keeps quoted filenames
import pickle               # need this for serializing objects
import os                   # Need this for reading from the file system
import os.path              # Used to read the file
import sys                  # Used to get ARGV (Argument values)
from mylib import message   # Python specific format to import custom module

# Global settings
DEFAULT_PORT = 5000
CONNECTION_TIMEOUT = 10  # seconds
RECEIVE_BUFFER = 1024  # bytes
SEND_BUFFER = 1024  # bytes


class FTPServer:
    def __init__(self, server_port=DEFAULT_PORT):
        self.server_port = server_port
        self.server_socket = None

    def open_socket(self):
        # Open a socket
        self.server_socket = socket(AF_INET, SOCK_DGRAM)

        # Listen on serverPort for messages
        self.server_socket.bind(('', self.server_port))

        # Wait for input, and respond
        print("The server is ready to receive")

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

    def __check_command(self, command, connection_socket, address):
        if not command:
            self.__log_connection_data("Empty command!", address)
            return

        # Split the string on spaces, if there are quotes, spaces inside that are preserved
        command_and_args = shlex.split(command)

        if command_and_args[0].lower() == "list":
            self.__send_list(connection_socket, address)

        elif command_and_args[0].lower() == "get":
            self.__send_file_details(connection_socket, command_and_args, address)

        elif command_and_args[0].lower() == "exit":
            self.__log_connection_data("Client requested disconnect.", address)
            self.server_socket.close()

        else:
            self.__log_connection_data("Invalid command!", address)
            e_list = pickle.dumps("Invalid command! " + command_and_args[0].lower())
            connection_socket.sendto(e_list, address)

    def __send_list(self, connection, address):
        self.__log_connection_data("Listing directory contents", address)
        my_path = os.getcwd()
        f_list = os.listdir(my_path)
        e_list = pickle.dumps(f_list)
        connection.sendto(e_list, address)

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
    print("Usage: " + script_name + " PORT_NUMBER")

def main(argv):
    script_name = argv[0]  # Snag the first argument (The script name
    port_to_use = DEFAULT_PORT

    # Make sure we have exactly
    if len(argv) == 2:
        port_to_use = int(argv[1])
    elif len(argv) > 2:
        sys.stderr.write("ERROR: Too many arguments specified\n\n")
        print_help(script_name)
        sys.exit(2)

    server = FTPServer(port_to_use)
    server.open_socket()
    server.listen()


# Start the server
if __name__ == "__main__":
    main(sys.argv)
