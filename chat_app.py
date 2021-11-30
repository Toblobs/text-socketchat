#A Synergy Studios Project
#Base Code contributed by - https://www.thepythoncode.com/article/make-a-chat-room-application-in-python

version = '1.2.1'
print('_' * 30)

def client_code():
    import socket
    from time import sleep
    from threading import Thread
    from datetime import datetime
    
    ### SERVER CONNECT
    SERVER_HOST = input("Please enter a host IP: ") #Local - "127.0.0.1"
    SERVER_PORT = 6969 #Port  - 6969

    

    if SERVER_HOST.lower() == '/local':
        SERVER_HOST = "127.0.0.1"

    seperator_token = "<SEP>"

    s = socket.socket()
    print("[*] Connecting to {}:{}...".format(SERVER_HOST, SERVER_PORT))

    try:
        s.connect((SERVER_HOST, SERVER_PORT))
        print("[+] Connected.")
        name = input("Please enter a name: ")
        
    except BaseException as e:
        print("[!] Error: {}".format(e))
        quit()

    slow_chat = 0

    def listen_for_messages():
        while True:

            try:
                message = s.recv(1024).decode()
                print("\n" + message)

                if message.split()[0] == '[>///][SERVER]':

                    for m in message.split():
                        print(m)
                        
                    if message.split()[4] == '/slow_chat':
                        slow_chat = int(message.split()[6])
                    if message.split()[4] == '/ban':
                        if name == message.split()[6]:
                            s.close()
                        
                    
                
            except BaseException as e:
                print("[!] Error: {}".format(e))
                quit()


    t = Thread(target=listen_for_messages)
    t.daemon = True #Ends when main thread ends
    t.start()

    print('Start chatting! To exit the program, type [Q]')
    print('-' * 30)

    while True:
        print()
        to_send = input()
        
        if to_send.lower() == '[q]': #Quit
            s.close()
        
        time_sent = datetime.now().strftime('%H:%M') #Datetime
        to_send = "~ {}{}{} [{}]".format(name, seperator_token, to_send, time_sent)

        try:
            sleep(slow_chat)
            s.send(to_send.encode())

        except BaseException as e:
            print("[!] Error: {}".format(e))
            quit()



def server_code():
    import socket
    from threading import Thread
    from datetime import datetime
    from random import randint

    ### SETUP
    MY_IP = socket.gethostbyname(socket.gethostname())
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 6969
    MOD_PASS = '/mod ' + str(randint(111111, 999999))
    seperator_token = "<SEP>"
    max_users = 10

    client_sockets = set()
    client_names = {}
    moderator_list = []
    commands = ['/mod', '/slow_chat', '/ban']
    
    s = socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    s.bind((SERVER_HOST, SERVER_PORT))
    s.listen(max_users)

    time_sent = datetime.now().strftime('%H:%M')
    
    print("[*] Listening as {}:{} at {}".format(SERVER_HOST, SERVER_PORT, time_sent))
    print("[*] Server IP: {}".format(MY_IP))
    print("[?] Mod Pass: {}".format(MOD_PASS))

    
    ### RUNNING SCRIPT
    def listen_for_client(cs):
        """This function listens for a message from cs.
        When a message is recieved, broadcast it to all other clients."""

        while True:
            
            try:
                msg = cs.recv(1024).decode()

            except BaseException as e:

                left_chat_msg = "[*][SERVER] {} has left the chat".format(client_address)
                print("[*][SERVER] {} has left the chat: {}".format(client_address, e))
                
                for client_socket in client_sockets:
                    if client_socket != cs:
                        client_socket.send(left_chat_msg.encode())

                break


            else:

                raw_msg = msg.split('>')[1]
                
                #print(raw_msg)

                comm = 'undefined'
                details = 'null'

                if raw_msg[0] == '/':
                    comm = raw_msg.split()[0]
                    details = raw_msg.split()[1]

                    if comm in commands:
                        raw_msg = raw_msg.split()[0] + " " + raw_msg.split()[1]

                    print('[>/] {} sent [comm:details] {}:{} as raw {}'.format(client_address, comm, details, raw_msg))
                              
                    
                if comm != 'undefined':
                    if comm in commands:

                        if client_address in moderator_list:
                            #print('a command and in mod')

                            send_comm = '[>///][SERVER] {} set {} as {}'.format(client_address, comm, details)
                            print(send_comm)

                            for client_socket in client_sockets:
                                client_socket.send(send_comm.encode())
                                

                        else:

                            #print('a command but not in mod')

                            if raw_msg == MOD_PASS:
                                
                                moderator_list.append(client_address)
                               
                                
                                mod_msg = "[*][SERVER] {} has become a moderator - {}".format(client_address, moderator_list)
                                print(mod_msg)

                                for client_socket in client_sockets:
                                    client_socket.send(mod_msg.encode())
                                        
                                #break

                                #MOD_PASS = '/mod ' + str(randint(111111, 999999))
                                #print("[?] Mod Pass: {}".format(MOD_PASS))
                                
                                

                            elif raw_msg[0:4] == '/name':
                                client_names[client_address] = raw_msg[5:]
                                print('[@] Client Names Dict[{}] = {}'.format(client_address, raw_msg[5:]))
                                
                else:
                    #print('not a command')
                    
                    msg = msg.replace(seperator_token, ": ")
                    print('[>] {} sent {}'.format(client_address, msg)) #Replace token with :

                    for client_socket in client_sockets:

                        try:
                            if client_socket != cs:
                                client_socket.send(msg.encode())
                        except:
                            client_socket.close()

                    
    while True:
        
        #Adding clients
        
        client_socket, client_address = s.accept()
        print("[+] {} connected.".format(client_address))
        
        client_sockets.add(client_socket)

        #join_msg = "[*][SERVER] {} has joined the chat".format(client_address)
                
        #for client_socket in client_sockets:
            #client_socket.send(join_msg.encode())

        #break
        
        t = Thread(target = listen_for_client, args = (client_socket,))
        t.daemon = True #Ends when main thread ends
        t.start()

    for cs in client_sockets:
        cs.close() #Close client connections

    s.close() #Close server



def main():
    print()
    run_menu = input('[>][CONNECT MENU]: {/server} {/client} ')

    if run_menu.lower() == '/server':

        print('-' * 30)
        server_code()

    elif run_menu.lower() == '/client':

        print('-' * 30)
        client_code()

    else:
        print('[!] Not a valid menu function!')
        main()

if __name__ == '__main__':
    main()
