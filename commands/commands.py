from utilities.common_ut import send_msg
from utilities.server_ut import process_alive, launch_script_minimized
import time

def execute_commands(command_list, processes_dict):
    kill_server= False

    for command in command_list:

        if command[0] == 'kill':
            if processes_dict[command[1]]['socket'] != None:
                send_msg(processes_dict[command[1]]['socket'], 'kill')

        elif command[0] == 'kill_server':
            kill_server = True

        elif command[0] == 'start':
            if processes_dict[command[1]]['process'] != None:
                if process_alive(processes_dict[command[1]]['process']):
                    continue
            if processes_dict[command[1]]['start_blocked_at'] == None:
                processes_dict[command[1]]['process'] = launch_script_minimized(command[1])
            elif processes_dict[command[1]]['start_blocked_at'] != None:
                if processes_dict[command[1]]['start_blocked_at'] + processes_dict[command[1]]['minutes_blocked'] * 60 <= time.time():
                    processes_dict[command[1]]['start_blocked_at'] = None
                    processes_dict[command[1]]['minutes_blocked'] = None
                    processes_dict[command[1]]['process'] = launch_script_minimized(command[1])
            
        elif command[0] == 'block':
            processes_dict[command[1]]['start_blocked_at'] = time.time()
            processes_dict[command[1]]['minutes_blocked'] = int(command[2])

        elif command[0] == 'remove_block':
            processes_dict[command[1]]['start_blocked_at'] = None
            processes_dict[command[1]]['minutes_blocked'] = None

        elif command[0] == 'discord_get_processes':
            if processes_dict['discordb.py']['socket'] != None:
                active_processes = []
                for process_name in processes_dict:
                    if processes_dict[process_name]['process'] != None:
                        if process_alive(processes_dict[process_name]['process']):
                            active_processes.append(process_name)
                msg = f'Active processes: {active_processes}'
                send_msg(processes_dict['discordb.py']['socket'], msg)

       
    command_list.clear()
    return processes_dict, kill_server
