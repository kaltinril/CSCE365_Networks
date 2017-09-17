from socket import *    # Used for sending and receiving information over sockets
import shlex            # need this for it's split that keeps quoted filenames
import pickle           # need this for serializing objects

class FTPServer:
    def __init__(self, server_port=5000):
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
        while True:
            message, client_address = self.server_socket.recvfrom(2048)
            modified_message = message.decode()
            self.__check_command(modified_message, client_address)
            self.server_socket.sendto(modified_message.upper().encode(), client_address)

    # Private methods
    def __check_command(self, command, client_address):
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
            serialized_list = pickle.dumps(f_list)
            # connectionSocket.send(serialized_list)
            # self.server_socket.sendto(modified_message.upper().encode(), client_address)

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


def main():
    server = FTPServer(12000)
    server.open_socket()
    server.listen()


# Start the server
main()
