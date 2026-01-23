import time
import os
import queue
from pynput import keyboard
import threading

run = True

alarm_queue = queue.Queue()

def timethread():
    global run
    alarms = []
    while alarms and run:
        try: new_alarm = alarm_queue.get_nowait()
        except queue.Empty: pass
        else: alarms.append(new_alarm)
        
        for alarm in alarms:
            if alarm[0] >= time.time():
                alarms.remove(alarm)
                alarm[1](*alarm[2])

time_thread = threading.Thread(target=timethread)

def timed_event(unixtime:int, func, *args):
    alarm_queue.put((unixtime, func, args))
    if not time_thread.is_alive():
        time_thread = threading.Thread(target=timethread)
        time_thread.start()

def exec_file(file:str):
    with open(file, 'r') as f:
        code = f.read()
        exec(code)
        
def exit():
    global run
    run = False

def key_pressed(key):
    global key_queue
    char = key.name
    key_queue.put(char)

key_queue = queue.Queue()
listener = keyboard.Listener(on_press=key_pressed)
listener.start()

def flush_keyqueue():
    flush = True
    while flush:
        try: key_queue.get_nowait()
        except queue.Empty: return

def option(chars:list, funcs:list):
    flush_keyqueue()
    listen = True
    while listen:
        key = key_queue.get()
        if key in chars:
            funcs[chars.index(key)]()


def clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')