from socket  import *
import sys
import pickle
import threading
import const #- addresses, port numbers etc. (a rudimentary way to replace a proper naming service)

def authentication():
    i = 1
    while(i < 4):
        if(i == 2): print('You have just one more try!')
        username = input('Enter your username: ')
        password = input('Enter your password: ')
        if(const.registry[username] and const.registry[username][2] == password):
            print('Welcome ' + username + '\n')
            return username
        print('Wrong username or password!')
        if(i == 2): sys.exit(1)
        i= i + 1

class RecvHandler(threading.Thread):
  def __init__(self, sock):
    threading.Thread.__init__(self)
    self.client_socket = sock

  def run(self):
    while True:
        #print('Client receiving handler is ready.')
        (conn, addr) = self.client_socket.accept() # accepts connection from server
        #print('Server connected to me.')
        marshaled_msg_pack = conn.recv(1024)   # receive data from server
        msg_pack = pickle.loads(marshaled_msg_pack) # unmarshal message pack
        print("You got a new message!\nMESSAGE: " + msg_pack[0] + " - FROM: " + msg_pack[1] + '\n')
        conn.send(pickle.dumps("ACK")) # simply send the server an Ack to confirm
        conn.close()
    return # We need a condition for graceful termination

me = authentication()
client_sock = socket(AF_INET, SOCK_STREAM) # socket for server to connect to this client
my_ip = const.registry[me][0]   # If using a proper naming service, client should know its
my_port = const.registry[me][1] # addresses (which it would register in the ns)
client_sock.bind((my_ip, my_port))
client_sock.listen(5)
#
# Put receiving thread to run
recv_handler = RecvHandler(client_sock)
recv_handler.start()
#
# Handle interactive loop
while True:
    server_sock = socket(AF_INET, SOCK_STREAM) # socket to connect to server
    dest = input("ENTER DESTINATION: ")
    msg = input("ENTER MESSAGE: ")
    #
    # Connect to server
    try:
        server_sock.connect((const.CHAT_SERVER_HOST, const.CHAT_SERVER_PORT))
    except:
        print("Server is down. Exiting...")
        exit(1)
    #
    # Send message and wait for confirmation
    msg_pack = (msg, dest, me)
    marshaled_msg_pack = pickle.dumps(msg_pack)
    server_sock.send(marshaled_msg_pack)
    marshaled_reply = server_sock.recv(1024)
    reply = pickle.loads(marshaled_reply)
    if reply != "ACK":
        print("Error: Server did not accept the message (dest does not exist?)")
    else:
        #print("Received Ack from server")
        pass
    server_sock.close()
