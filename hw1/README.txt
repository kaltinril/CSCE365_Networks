server_ftp.py
  Server has all requested features implemented.
  
  Usage: python3 server_ftp.py <port_number>
    port_number is optional and defaults to 5000
  
  Passing too many arguments on the command line will print an error and the example usage
  
  Because of the blocking that the socket.accept() does, to exit the server:
    Press CTRL+C, and connect a client
    OR
    Close the command window/terminal

client_ftp.py
  Client has all requested features implemented
  
  Usage: python3 client_ftp.py <server_address> <port_number>
    server_address is required (All examples show this to be the case, request was not made for optional argument)
    port_number is required (All examples show this to be the case, request was not made for optional argument)
  
  To exit type exit
  To get a list of files type list
  To retrieve a file type get <filename>
    NOTE: If the filename you wish to get has spaces, use double quotes  get "my file name.txt"