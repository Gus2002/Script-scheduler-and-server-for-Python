import subprocess

def accept_conn(server_socket):
    try:
        clientsocket = server_socket.accept()[0]
        return clientsocket
    except Exception as e: 
        return None 

def launch_script_minimized(script_name):
    SW_MINIMIZE = 6
    info = subprocess.STARTUPINFO()
    info.dwFlags = subprocess.STARTF_USESHOWWINDOW
    info.wShowWindow = SW_MINIMIZE

    process = subprocess.Popen(['python', script_name], startupinfo=info, creationflags=subprocess.CREATE_NEW_CONSOLE)
    return process

def process_alive(process):
    if process.poll() == None:
        return True
    else:
        return False