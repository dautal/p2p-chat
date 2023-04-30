import socket
import threading
import os
import random

UDP_MAX_SIZE = 65535

# availiable commands in the chat
COMMANDS = (
 '/members',
 '/connect',
 '/exit',
 '/myid'
)

def listen(s: socket.socket):
    while True:
      # getting message and address
      msg, addr = s.recvfrom(UDP_MAX_SIZE)
      msg_port = addr[-1] # get the port number from the sender address
      msg = msg.decode('ascii')
      allowed_ports = threading.current_thread().allowed_ports
      
      # ignore messages if client did not connect to the chat
      if msg_port not in allowed_ports:
        continue
      
      # ignore empty messages
      if not msg:
        continue
      
      # processing command messages
      if '__' in msg:
        command, content = msg.split('__')
        if command == 'members':
          for n, member in enumerate(content.split(';'), start=1):
            print('\r\r' + f'{n}) {member}' + '\n' + 'you: ', end='')
      # print messages from chat clients
      else:  
        peer_name = f'client{msg_port}'
        print('\r\r' + f'{peer_name}: ' + msg + '\n' + f'you: ', end='')

# function to start listening thread
def start_listen(target, socket, host, port):
  th = threading.Thread(target=target, args=(socket,), daemon=True)
  th.start()
  return th

# function to connect to the chat and start sending/receiving messages
def connect(host: str = '127.0.0.1', port: int = 3000):
    own_port = random.randint (8000, 9000)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, own_port))

    listen_thread = start_listen(listen, s, host, port)
    allowed_ports = [port]
    listen_thread.allowed_ports = allowed_ports
    sendto = (host, port)
    s.sendto('__join'.encode('ascii'), sendto) # send join message to server
    while True:
      msg = input(f'you: ')

      #check if message is a command
      command = msg.split(' ')[0]
      if command in COMMANDS:
        if msg == '/members':
          s.sendto('__members'.encode('ascii'), sendto)

        if msg == '/exit': 
          peer_port = sendto[-1]
          allowed_ports.remove(peer_port)
          sendto (host, port)
          print(f'Disconnect from client{peer_port}')

        # connect to another chat client
        if msg.startswith('/connect'):
          peer = msg.split(' ')[-1]
          peer_port = int(peer.replace('client', ''))
          allowed_ports.append(peer_port)
          sendto = (host, peer_port)
          print(f'Connect to client{peer_port}')
        
        # shpw the id of the client
        if msg.startswith('/myid'):
          print("You are client" + str(own_port))
      
      # if message is not a command send it to the chat
      else: 
        s.sendto(msg.encode('ascii'), sendto)

if __name__ == '__main__':
    os.system('clear')
    print('Welcome to chat!')
    connect()
