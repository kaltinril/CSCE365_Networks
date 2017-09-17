from socket import *    # Used for sending and receiving information over sockets
import shlex            # need this for it's split that keeps quoted filenames
import pickle           # need this for serializing objects
import os               # Need this for reading from the file system
import os.path
import threading

# Global settings
DEFAULT_PORT = 5000
CONNECTION_TIMEOUT = 60  # seconds
RECEIVE_BUFFER = 1024  # bytes
SEND_BUFFER = 1024  # bytes


class FTPServer:
    def __init__(self, server_port=DEFAULT_PORT):
        self.server_port = server_port
        self.server_socket = None
        self.conn_socket = None
        self.threads = []

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
        while True:
            self.conn_socket, address = self.server_socket.accept()
            self.conn_socket.settimeout(CONNECTION_TIMEOUT)

            # Start a new thread for this accepted connection
            t = threading.Thread(target=self.worker, args=(self.conn_socket, address))
            self.threads.append(t)
            t.start()

    def worker(self, connection, address):
        # Loop until the end of time
        while True:
            try:
                message = connection.recv(RECEIVE_BUFFER)
                message = message.decode()
                self.__check_command(message, connection)
            except:
                if connection.fileno() != -1:
                    connection.close()
                return False


    # Private methods
    def __check_command(self, command, connection_socket):
        if not command:
            print("Empty command!")
            return

        # Split the string on spaces, if there are quotes, spaces inside that are preserved
        command_and_args = shlex.split(command)
        print(command_and_args)

        if command_and_args[0].lower() == "list":
            self.__send_list(connection_socket)

        elif command_and_args[0].lower() == "get":
            self.__send_file_details(connection_socket, command_and_args)

        elif command_and_args[0].lower() == "exit":
            print("Exit")
            self.conn_socket.close()

        else:
            print("Unknown command! " + command)

    def __send_list(self, connection):
        print("Listing directory contents")
        my_path = os.getcwd()
        f_list = os.listdir(my_path)
        e_list = pickle.dumps(f_list)
        connection.send(e_list)

    def __send_file_details(self, connection, command_and_args):
        print("Get a file")
        if len(command_and_args) < 2:
            e_list = pickle.dumps("Error: No filename provided with get!")
            connection.send(e_list)
        else:
            filename = command_and_args[1]
            if os.path.exists(filename):
                try:
                    size = os.stat(filename).st_size
                    e_list = pickle.dumps("sending " + filename + " size " + str(size))
                    connection.send(e_list)

                    self.__send_file(connection, filename)

                except FileNotFoundError:
                    # doesn't exist
                    e_list = pickle.dumps("Error: File not found! " + filename)
                    connection.send(e_list)
                except:
                    print("Unexpected error:", sys.exc_info()[0])
                    e_list = pickle.dumps("Error: Unknown error with file! " + filename)
                    connection.send(e_list)
            else:
                e_list = pickle.dumps("Error: File not found! " + filename)
                connection.send(e_list)

    def __send_file(self, connection, filename):
        try:
            file = open(filename, 'rb')
            data = file.read(SEND_BUFFER)
            while data:
                connection.send(data)
                data = file.read(SEND_BUFFER)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            connection.send("Error: Unknown error reading file or sending file " + filename)

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
