
from socket import *

# Configuration
serverName = "localhost"
serverPort = 12000

# Open connection to server
clientSocket = socket(AF_INET, SOCK_DGRAM)

# Prompt user for input and send that to the Server
message = input("Input lowercase sentence:")
clientSocket.sendto(message.encode(), (serverName, serverPort))

# Receive a response from the Server and print it
modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
print(modifiedMessage.decode())

# Clean up
clientSocket.close()
