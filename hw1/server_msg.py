from socket import *

# Configure the server
serverPort = 12000

# Open a socket
serverSocket = socket(AF_INET, SOCK_DGRAM)

# Listen on serverPort for messages
serverSocket.bind(('', serverPort))

# Wait for input, and respond
print("The server is ready to receive")
while True:
    message, clientAddress = serverSocket.recvfrom(2048)
    modifiedMessage = message.decode().upper()
    serverSocket.sendto(modifiedMessage.encode(), clientAddress)

# Clean up
serverSocket.close()


