import os
import queue
from pathlib import Path
try: import pynput
except:
    os.system('pip install pynput')
    print('first time setup complete please restart')
    print('if this keeps showing run "python3 -m venv .venv" then run "source .venv/bin/activate" before running every time you run OS')
    quit(1)

key_queue = queue.Queue()

def key_press(key):
    try: char = key.char
    except AttributeError: char = key.name
    key_queue.put((char, True))

def key_release(key):
    try: char = key.char
    except AttributeError: char = key.name
    key_queue.put((char, False))

pynput.keyboard.Listener(key_press, key_release, True).start()

def flush_keyqueue():
    while not key_queue.empty():
        key_queue.get_nowait()

class FileSystem():
    def path(self, user_path: str) -> Path:
        path = (self.root / user_path).resolve(strict=False)

        if not path.is_relative_to(self.root):
            raise PermissionError("Invalid Directory")

        return path

    def __init__(self, root:str):
        self.root = Path(root).resolve()

    def mkdir(self, path:str):
        p = self.path(path)
        if not p.exists() and p.is_dir():
            p.mkdir(parents=True, exist_ok=True)
    
    def mkfle(self, file:str):
        f = self.path(file)
        if f.is_file() and f.parent.exists():
            with open(f, 'x'): pass

    def rmdir(self, path:str):
        p = self.path(path)
        if p.exists() and p.is_dir():
            p.rmdir()

    def rmfle(self, file:str):
        f = self.path(file)
        if f.is_file() and f.exists():
            os.remove(f)

    def lsdir(self, path:str):
        p = self.path(path)
        if p.is_dir() and p.exists:
            contents = sorted(p.iterdir(), key=lambda x: x.name)
            return contents
        else:
            return None
    
    def rdfle(self, file:str, offset:int = 0, size:int = 64000):
        f = self.path(file)
        if f.is_file():
            with open(f, 'rb') as fl:
                if f.stat().st_size > size:
                    fl.seek(offset - size / 2)
                    return fl.read(size).decode()
                else:
                    return fl.read().decode()

    def mk(self, path:str):
        p = self.path(path)
        if p.is_file(): self.mkfle(path)
        else: self.mkdir(path)

    def rm(self, path:str):
        p = self.path(path)
        if p.is_file(): self.rmfle(path)
        else: self.rmdir(path)

class Terminal():
    def clear(self):
        self.buffer = []
        self.update_last('')
        self.clear_screen()

    def get_size(self):
        self.size = os.get_terminal_size()
        self.size = (self.size.lines, self.size.columns)
        self.whitespace = (' ' * self.size[1] + '\n') * (self.size[0] + self.line_offset)
        return self.size

    def clear_screen(self):
        if os.name == 'nt':
            os.system('cls')
        else:
            os.system('clear')
        print("\033[0;0H", end = '')

    def __init__(self):
        self.buffer = []
        self.line_offset = 0
        self.last = ''
        self.get_size()
        self.clear_screen()
    
    def update(self):
        self.get_size()
        self.buffer = self.buffer[-self.size[0]:]
        print(f"\033[0;0H{self.whitespace}\033[0;0H{'\n'.join(self.buffer)}", end = '', flush = True)

        print('\r' + self.last, end = '')
    
    def print_noupdate(self, content:str, newline:bool = True):
        if newline or not self.buffer:
            self.buffer.append(content)
        else:
            self.buffer[-1] += content

    def print(self, content:str, newline:bool = True):
        self.print_noupdate(content, newline)
        self.update()

    def update_line(self, content:str, line:int = -1):
        self.buffer[line] = content
        self.update()

    def update_last(self, content:str, offset:int = 2):
        self.line_offset = offset
        if content:
            self.last = content
        else:
            self.last = ''
            self.line_offset = 0
        self.update()

    def input(self, prompt:str, offset:int = 2, return_keys:list = ['enter']):
        self.line_offset = offset
        flush_keyqueue()
        text = ''
        typing = True
        self.update()
        while typing:
            char, down = key_queue.get()
            if len(char) > 1:
                if char in return_keys and down:
                    out = text
                    typing = False
                elif char == 'backspace' and down:
                    text = text [:-1]
                    self.update_last(prompt + text)
                    self.update()
            else:
                if down:
                    text += char
                    self.update_last(prompt + text)
                    self.update()
        self.line_offset = 0
        self.update_last('')
        self.clear_screen()
        self.update()
        return text
    
    def option(self, prompt:str, return_keys:dict, offset:int = 2):
        flush_keyqueue()
        typing = True
        selected = 0
        buffer_old = self.buffer
        self.clear()
        options = list(return_keys.keys())
        self.update_last(prompt)
        while typing:
            self.clear()
            for i, o in enumerate(options):
                if i == selected:
                    self.print_noupdate(f'> {o} - {return_keys[o]}')
                    self.print_noupdate('')
                else:
                    self.print_noupdate(f'{o} - {return_keys[o]}')
                    self.print_noupdate('')
            self.update()
            char, down = key_queue.get()
            
            if down:
                match char:
                    case 'up':
                        if selected > 0:
                            selected -= 1
                    case 'down':
                        if selected < len(options) - 1:
                            selected += 1
                    case 'enter':
                        self.update_last(f'{prompt}{char}')
                        return options[selected]
                    case _:
                        if char in options and len(char) == 1:
                            self.update_last(f'{prompt}{char}')
                            return char
                        elif len(char) == 1:
                            self.update_last(f'{prompt}{char} is not a option')

        self.clear()
        self.buffer = buffer_old
    
