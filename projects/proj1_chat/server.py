import sys
import utils
import socket
import select

SOCKET_LIST = []
RECV_BUFFER = 4096 

def chat_server():
    host = "localhost"
    port = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
 
    channels = {}
    sock_name = {}
    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[])
      
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
             
            # a message from a client, not a new connection
            else:
                # process data recieved from client, 
                try:
                    # receiving data from the socket.
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        args = data.split()
                        if args[0] == '/list':
                            for channel in channels:
                                sock.send(channel + "\n")
                            continue
                        if args[0] == '/create':
                            if len(args) == 1:
                                sock.send(utils.SERVER_CREATE_REQUIRES_ARGUMENT + "\n")
                                continue
                            if args[1] in channels:
                                sock.send(utils.SERVER_CHANNEL_EXISTS.format(args[1]) + "\n")
                                continue
                            channels[args[1]] = []
                            continue
                        if args[0] == '/join':
                            if len(args) == 1:
                                sock.send(utils.SERVER_JOIN_REQUIRES_ARGUMENT + "\n")
                                continue
                            if args[1] not in channels:
                                sock.send(utils.SERVER_NO_CHANNEL_EXISTS.format(args[1]) + "\n")
                                continue
                            broadcast(server_socket, sock, SERVER_CLIENT_JOINED_CHANNEL.format(sock_name[sock])) 
                            for channel in channels:
                                if sock in channels[channel]:
                                    channels[channel].remove(sock)
                            channels[args[1]].append(sock)
                        if args[0][0] == '/':
                            sock.send(utils.SERVER_INVALID_CONTROL_MESSAGE.format(args[0]) + "\n")
                            continue
                        joinedChannel = False
                        for channel in channels:
                            if sock in channels[channel]:
                                joinedChannel = True
                        if not joinedChannel:
                            sock.send(utils.SERVER_CLIENT_NOT_IN_CHANNEL + "\n")
                            continue


                        # there is something in the socket
                        broadcast(server_socket, sock, "\r" + '[' + str(sock.getpeername()) + '] ' + data)  
                    else:
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)

                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, SERVER_CLIENT_LEFT_CHANNEL.format(sock_name[sock])) 

                # exception 
                except:
                    broadcast(server_socket, sock, "Client (%s, %s) is offline\n" % addr)
                    continue

    server_socket.close()
    
# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, message):
    for socket in SOCKET_LIST:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try :
                socket.send(message)
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)
 
if __name__ == "__main__":

    sys.exit(chat_server())   