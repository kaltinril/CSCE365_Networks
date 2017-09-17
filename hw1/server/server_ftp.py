from socket import *    # Used for sending and receiving information over sockets
import shlex            # need this for it's split that keeps quoted filenames
import pickle           # need this for serializing objects
import os               # Need this for reading from the file system

class FTPServer:
    def __init__(self, server_port=5000):
        self.server_port = server_port
        self.server_socket = None

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
        while True:
            conn_socket, addr = self.server_socket.accept()
            message = conn_socket.recv(1024)
            message = message.decode()
            self.__check_command(message, conn_socket)
            conn_socket.send(message.upper().encode())

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
            serialized_list = pickle.dumps(f_list)
            connection_socket.send(serialized_list)

        elif command_and_args[0].lower() == "get":
            print("Get a file")
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
    server = FTPServer(12000)
    server.open_socket()
    server.listen()


# Start the server
main()
