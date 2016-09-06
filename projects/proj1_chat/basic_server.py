import socket
import sys

class BasicServer(object):

    def __init__(self, port):
        self.port = int(port)
        self.socket = socket.socket()

    def accept(self):
    	self.socket.bind(("localhost", self.port))
    	self.socket.listen(5)
    	while 1:
	    	#accept connections from outside
	    	(clientsocket, address) = self.socket.accept()
	    	#now do something with the clientsocket
	    	#in this case, we'll pretend this is a threaded server
        	bytes_recd = 0
        	chunk = clientsocket.recv(2048)
        	print chunk

args = sys.argv
server = BasicServer(args[1])
server.accept()
