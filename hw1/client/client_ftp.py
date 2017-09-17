from socket import *


class FTPClient:
    def __init__(self, server_port=5000, server_name='localhost'):
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
        modified_message, server_address = self.client_socket.recvfrom(2048)
        return modified_message, server_address

    def __del__(self):
        # Clean up
        print("Closing the socket")
        self.client_socket.close()


def main():
    # Prompt user for input and send that to the Server
    msg_to_send = input("Input lowercase sentence:")

    # Create instance of client class, open socket, and send message
    server = FTPClient(12000)
    server.open_socket()
    server.send_message(msg_to_send)

    modified_message, server_address = server.get_message()
    print(modified_message.decode())


# Start the server
main()
