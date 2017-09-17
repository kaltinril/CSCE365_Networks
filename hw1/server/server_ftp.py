from socket import *


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
            modified_message = message.decode().upper()
            self.server_socket.sendto(modified_message.encode(), client_address)

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
