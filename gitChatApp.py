#A Synergy Studios Project
#Base Code contributed by - https://www.thepythoncode.com/article/make-a-chat-room-application-in-python

version = '1.0.1'

import socket
from time import sleep
from threading import Thread
from datetime import datetime
from random import randint


class Client():

    """A client that can connect to a server and send messages."""

    def __init__(self):

        self.SERVER_IP = {'LOCAL-1': '127.0.0.1', 'LOCAL-2': '192.168.1.12',
                          'SHSB-1': '', 'SHSB-2': ''}
        
        self.SERVER_PORT = 6969

        self.SERVER_TAG = None
        self.connected = False

        self.seperator_token = '<SEP>'

        self.banned_chars = ['_', '#', '<', '>']

        self.s = socket.socket()

        self.client_vars = {'name': None,
                            'ip': None}

        self.server_vars = {'wait': None,
                            'banned?': None}


    def start(self):
 
        self.sys_print('line-break-1')
        
        ## Trying to connect to a server 


        for s in self.SERVER_IP:
            
            connect_try = self.attempt_connect(s)

            if connect_try:
                break

            
        if not connect_try:

            ## Failed connections, quit
            
            print(f'[!] All server connection tries failed! Please try again later.')

            self.sys_print('line-break-1')

            sleep(5)
            quit()

        else:

            ## Connected to a server

            self.connected = True
            self.server_vars['banned'] = False

            self.sys_print('line-break-2')

            self.client_vars['name'] = input('Please type in a name: ')

            t = Thread(target = self.listen_for_messages)
            t.deamon = True
            t.start()

            print()
            print('Start chatting! Remember to visit our git at: https://github.com/Toblobs/text-socketchat')
            
            self.sys_print('line-break-1')

            while True:

                ## Chattin
                self.chat_along()

                sleep(self.server_vars[0])


    def check_connection(self):
        
        try:
            self.s.send('@CLIENT{self.seperator_token}_client_connection_test_')

        except:
            print(f'[!] Error recieved while checking connection: {e}')
            self.connected = False

    def chat_along(self):
        
        print()
        
        to_send = input()

        try:
            self.s.send(to_send.encode())

        except BaseExcpetion as e:
            print(f'[!] Error while attempting to send data: {e}')
            self.connected = False

    def handle_command(self):
        pass

    
    def listen_for_messages(self):

        while True:

            try:
                message = self.s.recv(2048).decode()
                print(message)

                if message.split(self.seperator_token)[0] == '@SERVER':

                    self.handle_command(message)

            except BaseException as e:
                
                print(f'[!] Error recieved while listening: {e}')
                self.connected = False
                break

    def attempt_connect(self, tag):

        self.SERVER_TAG = tag
        successful = False

        if self.SERVER_IP[tag]:

            print(f'[*] Trying to connect to <{tag}> server at {self.SERVER_IP[tag]}:{self.SERVER_PORT}...')

            try:
                self.s.connect((self.SERVER_IP[tag], self.SERVER_PORT))
                print(f'[+] Successful connection to {tag} server!')
                successful = True

            except BaseException as e:
                print(f'[!] Failed connection to {tag} server! ---> Error: {e}')

            print()
            
        return successful

    def sys_print(self, code):

        if code == 'line-break-1':
            print('_' * 50)
            print('-' * 50)

            print()

        elif code == 'line-break-2':
            print('-' * 50)

        else:
            pass


c = Client()

c.start()
