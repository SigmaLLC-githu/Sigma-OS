import kernel
import dotenv
import threading
import datetime
import time
import os

terminal = kernel.Terminal()
terminal.clear_screen()
terminal.print('Loading SigmaOS')

exit_code = 0

start_time = datetime.datetime.now()

terminal.print(f"System started at {start_time}")

kernel_options = dotenv.dotenv_values()

def get_option(key):
    try: return kernel_options['verbose']
    except KeyError: return None

def verbose_print(text):
    if get_option('verbose'):
        terminal.print(text)

filesystem = kernel.FileSystem('./root')

verbose_print('loaded filesystem')

class Shell():
    def __init__(self):
        self.options = []
        self.commands = {
            'make': lambda: filesystem.mk(self.options[0]),
            'remove': lambda: filesystem.rm(self.options[0]),
            'read': lambda: str(filesystem.rdfle(self.options[0], self.options[1]))
        }

def clock_thread():
    global active
    global now
    terminal.clear()
    while run:
        now = datetime.datetime.now()
        terminal.clear()
        terminal.print(f"{now.time().hour}:{now.time().minute}")
        active.wait(timeout=60 - now.second - now.microsecond / 1000000)

def clock():
    global active
    active = threading.Event()
    threading.Thread(target=clock_thread).start()
    time.sleep(1)
    kernel.flush_keyqueue()
    kernel.key_queue.get()
    active.set()
    return

def end_session():
    global run
    run = False


options = {
    't':'Open terminal (WIP)',
    'e':'End session',
    'c':'Open clock',
    'l':'Open app library (WIP)'
}

actions = {
    'e':end_session,
    'c':clock
}

run = True
while run:
    selected = terminal.option('>>', options)
    
    try: actions[selected]()
    except KeyError: pass

kernel.flush_keyqueue()
terminal.clear()
if exit_code:
    terminal.print(f'exiting with code {exit_code}')
else:
    terminal.print('exiting')
quit(exit_code)
    