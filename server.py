import socket
import time
import datetime
import re
import logging

from utilities.common_ut import send_msg, listen_recv
from utilities.server_ut import accept_conn, process_alive, launch_script_minimized
from commands.commands import execute_commands


def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((socket.gethostname(), 3284))
    s.settimeout(0.2) 
    s.listen(5)

    
    #add more processes here
    processes_dict = {
    'discordb.py': {
        'socket': None,
        'process': None,
        'start_blocked_at': None,
        'minutes_blocked': None,
        'launch_schedule': [(0,23)]
    },
    'test_client_script.py': {
        'socket': None,
        'process': None,
        'start_blocked_at': None,
        'minutes_blocked': None,
        'launch_schedule': None
    }
    }

    command_list = [] 
    kill_server = False

    logging.basicConfig(level=logging.INFO, filename='logs/server.log', filemode='a', format="%(asctime)s - %(levelname)s - %(message)s")
    try:
        while not kill_server:
            #Listening for incoming connection requests
            client_conn = accept_conn(s)
            if client_conn != None:
                client_conn.settimeout(0.2) 
                identified = False
                identification_timeout_it = 0

                while not identified and identification_timeout_it<60:
                    process_name = listen_recv(client_conn)
                    if type(process_name) is str:
                        for key in processes_dict:
                            if process_name == key:
                                processes_dict[process_name]['socket'] = client_conn
                                identified = True
                                send_msg(client_conn, 'identification_success')
                                print('Identified successfully')
                                break
                    identification_timeout_it+=1
            
            #listen for incoming messages loop  / check if socket connections are alive/ check if processes are alive
            for process_name in processes_dict:
                if processes_dict[process_name]['socket'] != None:
                    msg = listen_recv(processes_dict[process_name]['socket'])
                    if msg == False:
                        processes_dict[process_name]['socket'].close()
                        processes_dict[process_name]['socket'] = None
                    
                    #processing incoming commands and adding them to command list
                    elif type(msg) is str:
                        msg_cmds = re.findall('#[^#]*?!', msg) 
                        for i in range(len(msg_cmds)):
                            msg_cmds[i] = msg_cmds[i][1:-1].split(';') 
                            command_list.append(msg_cmds[i])
                        
            
                if processes_dict[process_name]['process'] != None:
                    if not process_alive(processes_dict[process_name]['process']):
                        processes_dict[process_name]['process'] = None
            
            
            #Executing incoming commands
            result = execute_commands(command_list, processes_dict)
            processes_dict = result[0]
            kill_server = result[1]
            command_list.clear()
                

            #schedule check loop
            for process_name in processes_dict:
                if type(processes_dict[process_name]['launch_schedule']) is list:
                    for duration in processes_dict[process_name]['launch_schedule']:
                        if datetime.datetime.now().hour >= duration[0] and datetime.datetime.now().hour <= duration[1]:
                            # checks to do if process is present
                            if processes_dict[process_name]['process'] != None:
                                if not process_alive(processes_dict[process_name]['process']):
                                    if processes_dict[process_name]['start_blocked_at'] != None:
                                        if processes_dict[process_name]['start_blocked_at'] + processes_dict[process_name]['minutes_blocked'] * 60 <= time.time():
                                            processes_dict[process_name]['start_blocked_at'] = None
                                            processes_dict[process_name]['minutes_blocked'] = None
                                            processes_dict[process_name]['process'] = launch_script_minimized(process_name)
                                            break
                                        else:
                                            break
                                    else:
                                        processes_dict[process_name]['process'] = launch_script_minimized(process_name)
                                        break
                            # checks to do if process is not present
                            else:
                                if processes_dict[process_name]['start_blocked_at'] != None:
                                    if processes_dict[process_name]['start_blocked_at'] + processes_dict[process_name]['minutes_blocked'] * 60 <= time.time():
                                        processes_dict[process_name]['start_blocked_at'] = None
                                        processes_dict[process_name]['minutes_blocked'] = None
                                        processes_dict[process_name]['process'] = launch_script_minimized(process_name)
                                        break
                                    else:
                                        break
                                else:
                                    processes_dict[process_name]['process'] = launch_script_minimized(process_name)
                                    break
                        
        #end of main loop
    except Exception as e:
        logging.exception('server')
        if processes_dict['discordb.py']['socket'] != None:
            send_msg(processes_dict['discordb.py']['socket'], 'Exception occurred in the server, check logs for traceback')
      
    #closing processes and sockets
    print('Sending kill command to all existing sockets')
    for process_name in processes_dict:     
        if processes_dict[process_name]['socket'] != None:
            send_msg(processes_dict[process_name]['socket'], 'kill')
            
    print('Waiting till all processes are closed')
    all_processes_closed = False
    while all_processes_closed == False:        
        all_processes_closed = True
        for process_name in processes_dict:
            if processes_dict[process_name]['process'] != None:
                if process_alive(processes_dict[process_name]['process']):
                    all_processes_closed = False
    
    print('Closing all sockets')
    for process_name in processes_dict:         
        if processes_dict[process_name]['socket'] != None:
            processes_dict[process_name]['socket'].close()

    s.close()
    


        

if __name__ == '__main__':
    main()
    
    