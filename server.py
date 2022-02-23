### The revamped Chattap
### A Synergy Studios Project

version_tag = '1.0.5'

import socket
from packet import Packet
from threading import Thread
from time import sleep

class SocketServer:

    """The server which sends and recieves messages."""

    def __init__(self, host: str, port: int, det):

        self.SERVER_HOST = host 
        self.SERVER_PORT = port 
        
        self.s = socket.socket()
        self.MY_IP = socket.gethostbyname(socket.gethostname())

        self.st = det[0]
        self.format = det[1]
        self.text_only = det[2]

        self.client_sockets = {}
        
        self.moderators = []
        self.sys_admin = None
        
        self.banned_addr = []

        self.all_commands = ('/message', '/name', '/whisper',
                             '/mod', '/ban', '/kick', '/mute', '/unmute', '/slowchat',
                             '/vertag', '/sys-notice')

        self.user_commands = ('/message', '/name', '/whisper', '/block')
        self.mod_commands = ('/mod', '/ban', '/kick', '/mute', '/unmute', '/slowchat')
        self.sys_commands = ('/vertag', '/sys-notice')

        self.max_users = 100
        self.byte_limit = 2048

        self.states = ('SETUP', 'RUNNING', 'STOPPED', 'MAINTENANCE')
        self.state = self.states[0]

    def start_server(self, start_loop = True):

        """Starts the server running."""

        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.SERVER_HOST, self.SERVER_PORT))
        self.s.listen(self.max_users)

        print(f'Running Chattap Server: v{version_tag}')
        
        print('_' * 30)
        print('-' * 30)
        print()

        print(f'[*] Binded <Server> to {self.SERVER_HOST}:{self.SERVER_PORT}')
        print(f'[*] Server Private IP Address: {self.MY_IP}')

        print()
        print('-' * 30)
        print()

        if start_loop:

            self.state = self.states[1]
            self.loop()

    def exit_server(self, error = None):

        """Exits the server with a optional error."""

        for key, value in self.client_sockets:
            key.close()

            if key in self.client_sockets:
                del self.client_sockets[key]

        self.s.close()

        self.state = self.states[2]
        print(f'[*] Server shutdown with error: {error}')

        quit()

    def send(self, cs, packet):

        """Sends data to a client in a specified format."""

        try:

            cs.send(packet.unwrap(self.st).encode(self.format))

        except:

            self.client_disconnected(cs)

    def broadcast(self, packet, special = False):

        """Broadcasts a message to all clients."""

        if not special:
            
            for cs in self.client_sockets:
                self.send(cs, packet)

        elif special[0] == 'except':

            for cs in self.client_sockets:

                if cs != special[1]:
                    self.send(cs, packet)

    def add_new_client(self, client_socket, client_address):
        
        """Adds a new client to the system."""
            
        self.client_sockets[client_socket] = (client_address, 'Guest')
        
        t = Thread(target = self.listen_for_client, args = (client_socket,), daemon = True)
        t.start()

        print(f'[+] Client {client_address} connected!')
        self.broadcast(Packet('/message', f'[*] Client {self.client_sockets[client_socket][1]} connected!'))
        
        if client_address[0] == '127.0.0.1' and len(self.moderators) == 0:
            self.add_moderator(client_socket)

        self.check_addr(client_socket, client_address)

    def client_disconnected(self, cs, e = None):

        """Cleanly exits a connection with a client."""

        sleep(0.15)

        if cs in self.client_sockets:

            client_tuple = self.client_sockets[cs]
            cs.close()

            print(f'[!] Client {client_tuple} disconnected: {e}')

            if cs in self.client_sockets:
                del self.client_sockets[cs]

            if cs in self.moderators:
                self.moderators.pop(self.moderators.index(cs))

            if self.sys_admin == cs:
                self.sys_admin = None

            self.broadcast(Packet('/message', f'[*] Client {client_tuple[1]} disconnected!'))

    def check_addr(self, cs, ca):

        """Checks if an address had been banned, and if so, kicks it."""

        if ca[0] in self.banned_addr:

            self.send(cs, Packet('/sys-notice', f'[SERVER] [!] You have been permanently banned from this server!'))
            self.send(cs, Packet('/sys-notice', f'[SERVER] [!] Please try to join another server!'))

            self.kick_client(cs, 'You have been permanently banned from this server!')

    def kick_client(self, cs, reason = None):

        """Kicks a client, with an optional message."""

        if reason:
            self.send(cs, Packet('/message', f'[SERVER] You have been kicked! Reason -> {reason}'))
            
        self.client_disconnected(cs, f'[SERVER] You have been kicked! Reason -> {reason}')

    def ban_client(self, cs, reason):

        """Bans a client (IP-Ban) with an message."""

        ca = self.client_sockets[cs][0][0]
        self.banned_addr.append(ca)

        self.send(cs, Packet('/message', reason))

        self.client_disconnected(cs, f'[SERVER] You have been permanently banned! Reason -> {reason}')

        print(self.banned_addr)
        
    def mute_client(self, cs, reason = None):

        """Mutes a client with an optional message."""

        self.send(cs, Packet('/muted', reason))

    def unmute_client(self, cs):

        """Unmutes a client."""

        self.send(cs, Packet('/unmuted', ''))

    def add_moderator(self, cs):

        """Adds a client to the moderator list."""

        sleep(0.1)

        if cs in self.client_sockets:

            self.moderators.append(cs)
            name = self.client_sockets[cs][1]

            if len(self.moderators) == 1: # Sys Admin
                self.sys_admin = cs

            sleep(0.1)

            print(f'[!] Client {name} has become a moderator!')
            self.broadcast(Packet('/message', f'[SERVER] [!] Client {name} has become a moderator!'))
            

    def examine_command(self, cs, packet):

        """Handles commands from the message."""

        ca = self.client_sockets[cs][0]
        name = self.client_sockets[cs][1]

        client_tuple = self.client_sockets[cs]

        ### All commands
        if packet.comm in self.all_commands:

            if '#' in packet.det:

                applied_client = packet.det.split('#')[0]
                further_details = packet.det.split('#')[1]

            else:

                applied_client = None
                further_details = None

            # Level 1 - User Commands
            if packet.comm in self.user_commands:

                if packet.comm == '/message':
                    
                    self.broadcast(Packet('/message', packet.det), ('except', cs))
                    print(f'[>] Client {client_tuple} has sent message: {packet.det}')

                elif packet.comm == '/name':

                    self.client_sockets[cs] = (ca, packet.det)
                    sleep(0.1)
                    print(f'[@] Client {client_tuple} set their name as: {packet.det}')

                elif packet.comm == '/whisper':

                    cs_to_send = self.get_cs(applied_client)

                    if cs_to_send:
                        self.send(cs_to_send, Packet('/whisper', (f'{name}#' + further_details)))
                        print(f'[>||] Client {client_tuple} whispered to {self.client_sockets[cs_to_send]}: {further_details}')
                            

            # Level 2 - Mod Commands
            elif packet.comm in self.mod_commands:
                
                if cs in self.moderators:

                    if packet.comm == '/ban':

                        cs_to_ban = self.get_cs(applied_client)

                        if cs_to_ban:

                            self.broadcast(Packet('/message', f'[SERVER] [!] Client {self.client_sockets[cs_to_ban]} was banned!'))

                            print(f'[/] Client {client_tuple} banned {self.client_sockets[cs_to_ban]} for reason: {further_details}')
                            self.ban_client(cs_to_ban, further_details)

                    elif packet.comm == '/kick':

                        cs_to_kick = self.get_cs(applied_client)

                        if cs_to_kick:

                            self.broadcast(Packet('/message', f'[SERVER] [!] Client {self.client_sockets[cs_to_kick]} was kicked!'))

                            print(f'[/] Client {client_tuple} kicked {self.client_sockets[cs_to_kick]} for reason: {further_details}')
                            self.kick_client(cs_to_kick, further_details)

                    elif packet.comm == '/mute':

                        cs_to_mute = self.get_cs(applied_client)

                        if cs_to_mute:
                            print(f'[/] Client {client_tuple} muted {self.client_sockets[cs_to_mute]} for reason: {further_details}')
                            self.mute_client(cs_to_mute, further_details)

                            self.broadcast(Packet('/message', f'[SERVER] [!] Client {self.client_sockets[cs_to_mute[1]]} was muted!'))

                    elif packet.comm == '/unmute':

                        cs_to_unmute = self.get_cs(applied_client)

                        if cs_to_unmute:
                            print(f'[/] Client {client_tuple} unmuted {self.client_sockets[cs_to_unmute]}')
                            self.unmute_client(cs_to_unmute)

                            self.broadcast(Packet('/message', f'[SERVER] [!] Client {self.client_sockets[cs_to_unmute[1]]} was unmuted!'))

                    elif packet.comm == '/slowchat':

                        new_slowchat = packet.det
                        
                        self.broadcast(Packet('/slowchat', new_slowchat))
                        

            # Level 3 - Sys Commands
            elif packet.comm in self.sys_commands:

                if packet.comm == '/vertag':
                    
                    if packet.det != version_tag:
                        
                        self.send(cs, Packet('/sys-notice', f'[SERVER] [!] Your Chattap is on version {packet.det}, however version {version_tag} is available!'))
                        self.send(cs, Packet('/sys-notice', '[SERVER] [!] Please update your chattap to the latest verison before chatting!'))

                        sleep(0.1)                        
                        self.kick_client(cs, reason = f'Wrong chattap version, update.')
                                  

        ### Non commands
        else:
            
            print(f'[>] Client {client_tuple} has sent unknown comm: {packet.det}')

    def listen_for_client(self, cs):

        """Listens for a client."""

        while True:

            if cs in self.client_sockets:

                try:

                    msg = cs.recv(self.byte_limit).decode().split(self.st)
                    
                    pk = Packet(msg[0], msg[1])

                except BaseException as e:

                    self.client_disconnected(cs, e)
                    break

                else:

                    self.examine_command(cs, pk)

    def loop(self):

        """Loops through adding and removing new clients."""

        while True:

            if self.state == self.states[0]: # SETUP
                pass

            elif self.state == self.states[1]: # RUNNING

                client_socket, client_address = self.s.accept()
                self.add_new_client(client_socket, client_address)
                
            elif self.state == self.states[2]:  # STOPPED
                pass

            elif self.state == self.states[3]: # MAINTENANCE
                pass

    def get_cs(self, name):

        """Returns the socket once given a user name."""

        for key, value in self.client_sockets.items():

            if value[1] == name:
                return key
            
                break

    def get_name(self, ca):

        """Returns the name once given a address."""

        for key, value in self.client_sockets:

            if value[0] == address:
                return value[1]

                break

    

s = SocketServer('0.0.0.0', 8989, ['%', 'UTF-8', True])
s.start_server()

