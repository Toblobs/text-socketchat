### The revamped Chattap
### A Synergy Stuidos Project

version_tag = '1.0.5'

import socket
from packet import Packet
from emoticons import *
from threading import Thread
from time import sleep
from datetime import datetime

class SocketClient:

    """The client which can send and recieve messages from the
       server it is connected to."""

    def __init__(self, host: str, port: int, det):

        self.SERVER_HOST = host
        self.SERVER_PORT = port


        self.s = socket.socket()
        self.MY_IP = socket.gethostbyname(socket.gethostname())

        self.st = det[0]
        self.format = det[1]

        self.states = ('SETUP', 'CONNECTED', 'DISCONNECTED')
        self.state  = self.states[0]

        self.name = my_name

        self.byte_limit = 2048
        
        self.command_inputs = {'slowchat': 2.5,
                               'char_limit': 500,
                               'muted': False}

        self.banned_chars = ['%', '[', ']', '@']

    def start_client(self, start_loop = True):

        """Starts the connection to the host."""

        #print(f'[*] Client Private IP Address: {self.MY_IP}')
        #print()
        
        print(f'[*] <Client> attempting connection to {self.SERVER_HOST}:{self.SERVER_PORT}')

        try:
            
            self.s.connect((self.SERVER_HOST, self.SERVER_PORT))

        except BaseException as e:

            self.exit_client(e)
        
        print(f'[+] Connection succesful to {self.SERVER_HOST}:{self.SERVER_PORT}!')
        print()

        self.state = self.states[1]
        
        self.send(Packet('/vertag', version_tag))
        self.send(Packet('/name', self.name))

        if start_loop:
            self.loop()


    def exit_client(self, error = None):

        """Exits the server with a optional error."""

        self.s.close()

        print(f'[*] Client shutdown with error: {error}')

        quit()

    def send(self, packet):

        """Sends data to the server."""

        self.s.send(packet.unwrap(self.st).encode(self.format))

    def examine_command(self, packet):

        """Handles commands from the message."""

        if packet.comm == '/message':

            print('\n' + '-> ' + packet.det)
            
        elif packet.comm == '/whisper':

            whisper_person = packet.det.split('#')[0]
            message = packet.det.split('#')[1]

            print('\n' + '-> ' + f'[WHISPER FROM {whisper_person}]: {message}')

        elif packet.comm == '/muted':
            
            print('\n' + '-> [!] You have been muted! Reason -> ' + packet.det)
            self.command_inputs['muted'] = True

        elif packet.comm == '/unmuted':

            print('\n' + '-> ' + '[!] You have been unmuted!')
            self.command_inputs['muted'] = False

        elif packet.comm == '/slowchat':

            print('\n' + '-> ' + f'[!] The slowchat has been set to {packet.det} seconds.')
            self.command_inputs['slowchat'] = int(packet.det)

        else:
            
            pass
        
    def listen_for_messages(self):

        """Listens for messages from the server."""

        while True:

            try:
                
                msg = self.s.recv(self.byte_limit).decode().split(self.st)

                pk = Packet(msg[0], msg[1])

                self.examine_command(pk)
                
            except BaseException as e:

                self.exit_client(e)

    def check_emoticons(self, message):

        """Checks for any emoticons and replaces them."""

        emoticon_message = ''
        found_emoticon = False

        for e in emoticons:

            if e in message:

                found_emoticon = True
                
                emoticon_message = message.replace(e, emoticons[e])

        if found_emoticon:
            return emoticon_message

        else:
            return message


    def loop(self):

        """Loops around, sending and receiving messages."""

        print('-' * 30)
        print()

        print('To send a private message: /whisper <name_of_person>#<message>')
        print('To change your name: /name <new_name>')
        print()

        print('-' * 30)
        print()

        t = Thread(target = self.listen_for_messages)
        t.daemon = True
        t.start()

        self.send(Packet('/name', self.name))
        
        while True:

            sleep(self.command_inputs['slowchat'])
            
            message = input()

            message = self.check_emoticons(message)

            if not self.command_inputs['muted'] and message != '' and not(any(char in message for char in self.banned_chars)):

                pk = None

                if '/' not in message:

                    time_now = datetime.now().strftime('%H:%M')
                    message = f'{self.name}: ' + message
                    
                    pk = Packet('/message', message)

                else:

                    command_split = message.split()
                    
                    command = command_split[0]
                    details = ' '.join(command_split[1:])

                    pk = Packet(command, details)

                    if command == '/name':
                        self.name = details

                self.send(pk)
                
            elif self.command_inputs['muted']:
                
                print('[!] You have been muted! Please wait to be unmuted.')

            elif message == '':

                print("[!] You can't send a message with no text!")

            elif any(char in message for char in self.banned_chars):

                print("[!] You can't send a message with any of the characters ", self.banned_chars, " inside of it!")
            

print(f'Running Chattap Client: v{version_tag}')
print('_' * 30)
print('-' * 30)
print()

server = input('Please input a host: ')
port = input('Please input a port: ')

print()
print('-' * 30)
print()

my_name = input('Please input a name: ')

print()

if server == '/local':
    server = '127.0.0.1'

s = SocketClient(str(server), int(port), ['%', 'UTF-8'])
s.start_client()
    
