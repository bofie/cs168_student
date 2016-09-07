import sys
import utils
import socket
import select
from client_split_messages import pad_message

SOCKET_LIST = []
RECV_BUFFER = 4096 
channels = {}

def chat_server():
    host = "localhost"
    port = int(sys.argv[1])
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
 
    # add server socket object to the list of readable connections
    SOCKET_LIST.append(server_socket)
 
    sock_name = {}
    partial_message = ""
    while 1:

        # get the list sockets which are ready to be read through select
        # 4th arg, time_out  = 0 : poll and never block
        ready_to_read,ready_to_write,in_error = select.select(SOCKET_LIST,[],[])
      
        for sock in ready_to_read:
            # a new connection request recieved
            if sock == server_socket: 
                sockfd, addr = server_socket.accept()
                SOCKET_LIST.append(sockfd)
                first_message = True
            # a message from a client, not a new connection
            else:
                channelrn = None
                for channel in channels:
                    if sock in channels[channel]:
                        channelrn = channel
                try:
                    data = sock.recv(RECV_BUFFER)
                    if data:
                        # print "received data length: " + str(len(data))
                        # print "partial m length: " + str(len(partial_message))
                        # print "received data: " + str(len(data)) + data
                        # print "partial m : " + str(len(partial_message)) +  partial_message
                        combined = partial_message + data
                        if len(combined) < utils.MESSAGE_LENGTH:
                            partial_message = combined
                            continue
                        if len(partial_message) < utils.MESSAGE_LENGTH and len(combined) >= utils.MESSAGE_LENGTH:
                            partial_message = (combined)[utils.MESSAGE_LENGTH:]
                            data = (combined)[:utils.MESSAGE_LENGTH]
                        data = data.rstrip()
                        # print "received data after stripping: " + str(len(data)) + data
                        args = data.split()
                        if args == []:
                            continue
                        if first_message:
                            sock_name[sock] = args[0]
                            first_message = False
                            continue
                        if args[0] == '/list':
                            for channel in channels:
                                sock.sendall(pad_message(channel + "\n"))
                            continue
                        if args[0] == '/create':
                            if len(args) == 1:
                                sock.sendall(pad_message(utils.SERVER_CREATE_REQUIRES_ARGUMENT + "\n"))
                                continue
                            if args[1] in channels:
                                sock.sendall(pad_message(utils.SERVER_CHANNEL_EXISTS.format(args[1]) + "\n"))
                                continue
                            channels[args[1]] = []
                            for channel in channels:
                                if sock in channels[channel]:
                                    channels[channel].remove(sock)
                            channels[args[1]].append(sock)
                            continue
                        if args[0] == '/join':
                            if len(args) == 1:
                                sock.sendall(pad_message(utils.SERVER_JOIN_REQUIRES_ARGUMENT + "\n"))
                                continue
                            if args[1] not in channels:
                                sock.sendall(pad_message(utils.SERVER_NO_CHANNEL_EXISTS.format(args[1]) + "\n"))
                                continue
                            for channel in channels:
                                if sock in channels[channel]:
                                    channels[channel].remove(sock)
                            channels[args[1]].append(sock)
                            broadcast(server_socket, sock, args[1], utils.SERVER_CLIENT_JOINED_CHANNEL.format(sock_name[sock]) + "\n")
                            continue
                        if args[0][0] == '/':
                            sock.sendall(pad_message(utils.SERVER_INVALID_CONTROL_MESSAGE.format(args[0]) + "\n"))
                            continue
                        joinedChannel = False
                        for channel in channels:
                            if sock in channels[channel]:
                                joinedChannel = True
                        if not joinedChannel:
                            sock.sendall(pad_message(utils.SERVER_CLIENT_NOT_IN_CHANNEL + "\n"))
                            continue

                        # there is something in the socket
                        broadcast(server_socket, sock, channelrn, "\r" + '[' + sock_name[sock] + '] ' + data + "\n")  
                    else:
                        # remove the socket that's broken    
                        if sock in SOCKET_LIST:
                            SOCKET_LIST.remove(sock)
                        # at this stage, no data means probably the connection has been broken
                        broadcast(server_socket, sock, channelrn, utils.SERVER_CLIENT_LEFT_CHANNEL.format(sock_name[sock]) + "\n") 

                # exception 
                except:
                    broadcast(server_socket, sock, channelrn, utils.SERVER_CLIENT_LEFT_CHANNEL.format(sock_name[sock]) + "\n") 
                    continue

    server_socket.close()
    
# broadcast chat messages to all connected clients
def broadcast (server_socket, sock, channel, message):
    if channel is None:
        return
    for socket in channels[channel]:
        # send the message only to peer
        if socket != server_socket and socket != sock :
            try :
                socket.sendall(pad_message(message))
            except :
                # broken socket connection
                socket.close()
                # broken socket, remove it
                if socket in SOCKET_LIST:
                    SOCKET_LIST.remove(socket)
                    channels[channel].remove(socket)
 
if __name__ == "__main__":

    sys.exit(chat_server())   