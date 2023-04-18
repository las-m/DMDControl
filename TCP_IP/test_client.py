import socket
import pickle 

HEADERSIZE = 10 

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientsocket.connect((socket.gethostname(), 2323))

bufsize = 16
while True:         
    full_msg = b''
    new_msg = True
    while True:    
        msg = clientsocket.recv(bufsize)
        if new_msg:
            print(f"New message length: {msg[:HEADERSIZE]}")
            msg_len = int(msg[:HEADERSIZE])
            new_msg = False

        full_msg += msg

        if len(full_msg)-HEADERSIZE == msg_len:
            print("full msg received.")
            print(full_msg[HEADERSIZE:])

            unpkd_msg = pickle.loads(full_msg[HEADERSIZE:])
            print(unpkd_msg)

            new_msg = True
            full_msg = b''

    if len(full_msg) > 0:
        print(full_msg)
