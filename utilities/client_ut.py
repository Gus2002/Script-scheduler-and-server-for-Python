import socket
from utilities.common_ut import send_msg, listen_recv

def connect_to_server(current_script_name):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), 3284))
    send_msg(s, current_script_name)
    s.settimeout(0.2)
    identification_timeout = 300
    id_iteration = 0
    while id_iteration < identification_timeout:
        msg = listen_recv(s)
        if type(msg) is str:
            if msg == 'identification_success':
                print('Successfully identified to server')
                return s
        id_iteration+=1
    
    return False