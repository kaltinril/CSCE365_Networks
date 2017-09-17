from socket import *    # Used for sending and receiving information over sockets
import shlex            # need this for it's split that keeps quoted filenames
import pickle           # need this for serializing objects
import os               # Need this for reading from the file system
import os.path


class FTPServer:
    def __init__(self, server_port=5000):
        self.server_port = server_port
        self.server_socket = None
        self.conn_socket = None

    def open_socket(self):
        # Open a socket
        self.server_socket = socket(AF_INET, SOCK_STREAM)

        # Listen on serverPort for messages
        self.server_socket.bind(('', self.server_port))

        # TCP - Begin listening for traffic
        self.server_socket.listen(1)

        # Wait for input, and respond
        print("The server is ready to receive")

    def listen(self):
        # Blocking wait for a "SYN" message
        self.conn_socket, address = self.server_socket.accept()

        # Loop until the end of time
        while True:
            message = self.conn_socket.recv(1024)
            message = message.decode()
            self.__check_command(message, self.conn_socket)


    # Private methods
    def __check_command(self, command, connection_socket):
        if not command:
            print("Empty command!")
            return

        # Split the string on spaces, if there are quotes, spaces inside that are preserved
        command_and_args = shlex.split(command)
        print(command_and_args)

        if command_and_args[0].lower() == "list":
            print("Listing directory contents")
            my_path = os.getcwd()
            f_list = os.listdir(my_path)
            print(f_list)
            e_list = pickle.dumps(f_list)
            connection_socket.send(e_list)

        elif command_and_args[0].lower() == "get":
            print("Get a file")
            if len(command_and_args) < 2:
                e_list = pickle.dumps("Error: No filename provided with get!")
                connection_socket.send(e_list)
            else:
                filename = command_and_args[1]
                if os.path.exists(filename):
                    try:
                        size = os.stat(filename).st_size
                        e_list = pickle.dumps("sending " + filename + " size " + str(size))
                        connection_socket.send(e_list)
                    except FileNotFoundError:
                        # doesn't exist
                        e_list = pickle.dumps("Error: File not found! " + filename)
                        connection_socket.send(e_list)
                    except:
                        print("Unexpected error:", sys.exc_info()[0])
                        e_list = pickle.dumps("Error: Unknown error with file! " + filename)
                        connection_socket.send(e_list)
                else:
                    e_list = pickle.dumps("Error: File not found! " + filename)
                    connection_socket.send(e_list)

        elif command_and_args[0].lower() == "exit":
            print("Exit")
        else:
            print("Unknown command! " + command)

    def __del__(self):
        # Clean up
        print("Closing the socket")
        self.server_socket.close()
        self.conn_socket.close()


def main():
    server = FTPServer(5000)
    server.open_socket()
    server.listen()


# Start the server
main()
