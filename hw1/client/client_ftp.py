from socket import *
import pickle
import shlex
import sys

# Global settings
DEFAULT_PORT = 5000
DEFAULT_SERVER = "localhost"
CONNECTION_TIMEOUT = 60  # seconds
RECEIVE_BUFFER = 768  # bytes
SEND_BUFFER = 768  # bytes


class FTPClient:
    def __init__(self, server_port=DEFAULT_PORT, server_name=DEFAULT_SERVER):
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

    def command_get(self, message, filename):
        # Send the get command to the server
        self.send_message(message)

        # Get the bytes that we will be receiving
        modified_message = self.get_message()
        f_list = pickle.loads(modified_message)
        print(f_list)

        if not f_list.startswith("Error:"):
            f_list = f_list.split()     # "sending filename.py size 123"
            size = f_list[len(f_list) - 1]
            self.__recv_file(filename, int(size))

    def __recv_file(self, filename, size):
        try:
            file = open(filename, 'wb')
            data = " - "
            received_data = 0
            while data:
                data = self.client_socket.recv(RECEIVE_BUFFER)
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

    def command_list(self, message):
        # Send the get command to the server
        self.send_message(message)

        modified_message = self.get_message()
        f_list = pickle.loads(modified_message)
        print(f_list)

    def __del__(self):
        # Clean up
        print("Closing the socket")
        self.client_socket.close()

def print_help(script_name):
    print("Usage:   " + script_name + " SERVER_NAME PORT_NUMBER")
    print("Example: " + script_name + " localhost 5000")

def main(argv):
    script_name = argv[0]  # Snag the first argument (The script name
    port_to_use = DEFAULT_PORT
    server_to_use = DEFAULT_SERVER

    # Make sure we have exactly
    if len(argv) != 3:
        sys.stderr.write("ERROR: Invalid number of arguments\n\n")
        print_help(script_name)
        sys.exit(2)
    else:
        server_to_use = argv[1]
        port_to_use = int(argv[2])

    # Create instance of client class, open socket, and send message
    print("Connecting to " + server_to_use + ":" + str(port_to_use))
    server = FTPClient(port_to_use, server_to_use)
    server.open_socket()

    running = True
    print("Enter a command (list, get, exit)")
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
                if len(command_and_args) > 1:
                    filename = command_and_args[1]
                    print("Requesting file : " + filename)
                    server.command_get(msg_to_send, filename)
                else:
                    print("Error: Must supply a filename with the get command!")

            elif command.lower() == "list":
                server.command_list(msg_to_send)


# Start the client
if __name__ == "__main__":
    main(sys.argv)
