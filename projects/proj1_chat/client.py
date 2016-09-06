import sys
import socket
import select
import utils
 
def chat_client():
    if(len(sys.argv) < 4) :
        print 'Usage : python chat_client.py hostname port'
        sys.exit()

    name = sys.argv[1]
    host = sys.argv[2]
    port = int(sys.argv[3])
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
     
    # connect to remote host
    try :
        s.connect((host, port))
    except :
        print utils.CLIENT_CANNOT_CONNECT.format(host, port)
        sys.exit()
     
    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX); sys.stdout.flush()
     
    while 1:
        socket_list = [sys.stdin, s]
         
        # Get the list sockets which are readable
        ready_to_read,ready_to_write,in_error = select.select(socket_list , [], [])
         
        for sock in ready_to_read:             
            if sock == s:
                # incoming message from remote server, s
                data = sock.recv(4096)
                if not data :
                    print "\n" + utils.CLIENT_SERVER_DISCONNECTED.format(host, port)
                    sys.exit()
                else :
                    #print data
                    sys.stdout.write(utils.CLIENT_WIPE_ME)
                    sys.stdout.write("\r" + data)
                    sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX); sys.stdout.flush()      
            
            else :
                # user entered a message
                msg = sys.stdin.readline()
                s.send(msg)
                sys.stdout.write(utils.CLIENT_MESSAGE_PREFIX); sys.stdout.flush() 

if __name__ == "__main__":

    sys.exit(chat_client())