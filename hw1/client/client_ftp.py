from socket import *
import pickle
import shlex

# Global settings
DEFAULT_PORT = 5000
CONNECTION_TIMEOUT = 60  # seconds
RECEIVE_BUFFER = 1024  # bytes


class FTPClient:
    def __init__(self, server_port=DEFAULT_PORT, server_name='localhost'):
        self.server_port = server_port
        self.server_name = server_name
        self.client_socket = None

    def open_socket(self):
        # Open a socket
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((self.server_name, self.server_port))
        print("Connection Opened with server")

    def send_message(self, message):
        self.client_socket.send(message.encode())

    def get_message(self):
        # Receive a response from the Server and print it
        modified_message = self.client_socket.recv(RECEIVE_BUFFER)
        return modified_message

    def __del__(self):
        # Clean up
        print("Closing the socket")
        self.client_socket.close()


def main():
    running = True
    print("Enter a command (list, get, exit)")
    server_ip = DEFAULT_PORT
    server_name = "localhost"

    # Create instance of client class, open socket, and send message
    server = FTPClient(server_ip, server_name)
    server.open_socket()

    while running:
        # Prompt user for input and send that to the Server
        msg_to_send = input(">:")

        command_and_args = shlex.split(msg_to_send)

        if len(command_and_args) > 0:
            command = command_and_args[0]

            if command.lower() == 'exit':
                # Send the exit command to the server
                server.send_message(msg_to_send)

                running = False
                continue  # exit this iteration
            elif command.lower() == "get":

                # Send the get command to the server
                server.send_message(msg_to_send)

                modified_message = server.get_message()
                f_list = pickle.loads(modified_message)
                print(f_list)
            elif command.lower() == "list":

                # Send the get command to the server
                server.send_message(msg_to_send)

                modified_message = server.get_message()
                f_list = pickle.loads(modified_message)
                print(f_list)


# Start the server
main()
