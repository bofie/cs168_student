import socket
server_socket = socket.socket()
server_socket.bind((ip, port))
server_socket.listen(int)
(new_sock, address) = server_socket.accept()
