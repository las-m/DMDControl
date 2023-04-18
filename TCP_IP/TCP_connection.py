import socket
import pickle

HEADERSIZE = 10

# AF_INET == ipv4
# SOCK_STREAM == TCP
serversocsket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

serversocket.bind((socket.gethostname(), 2323))
serversocket.listen(5)

while True:
    clientsocket, address = serversocket.accept()
    print(f"Connection from {address} has been established!")
    
    msg = "Connection successful!"
    msg = pickle.dumps(msg)
    print(msg)
    # make header (fixed-length-header)
    msg = bytes(f'{len(msg):<{HEADERSIZE}}', "utf-8") + msg

    clientsocket.send(msg)

    command_list = ['lc6500 = LightCrafter6500', 'lc6500.set_pattern_on_the_fly_mode()']
    msg = pickle.dumps(command_list)
    print(msg)
    # make header (fixed-length-header)
    msg = bytes(f'{len(msg):<{HEADERSIZE}}', "utf-8") + msg

    clientsocket.send(msg)

    #clientsocket.close()