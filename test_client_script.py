from utilities.common_ut import listen_recv
from utilities.client_ut import connect_to_server
import sys
import time
def main():
    sock = connect_to_server('test_client_script.py')
    run_client = True
    while run_client:
        msg = listen_recv(sock)
        if msg == False or msg == 'kill':
            sock.close()
            sys.exit()
        time.sleep(1)


if __name__ == '__main__':
    main()
    
    