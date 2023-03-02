
def send_msg(sock, message):
    tries = 3
    for i in range(tries):
        try:
            sent_state = sock.sendall(bytes(message, 'utf-8'))
            if sent_state == None:    
                return 'Success'
        except:
            if i < tries - 1:
                continue
            else:
                return 'Failure'

def listen_recv(socket):
    try:
        msg = socket.recv(1024)
        if not msg:
            return False
        final_msg = msg.decode('utf-8')
        return final_msg
    except Exception as e:
        return None