# Authors:
#
# Guilherme Henrique Pereira Serafini - 2021.1.08.048
# Vinícius Eduardo de Souza Honório - 2021.1.08.024

import socket

UDP_IP = input('Enter IP Address [blank for local]: ')
UDP_PORT = 12000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet|UDP

print("UDP Target Port: %s" % UDP_PORT)
print("Client Running: OK")

while True:
    MESSAGE = input()
    sock.sendto(MESSAGE.encode("utf-8"), (UDP_IP, UDP_PORT))

    data, addr = sock.recvfrom(2048)
 
    if(data.decode('utf-8') != '@started'):
        print(data.decode('utf-8'))
    else: # Receives file from Server.py
        sock.sendto('@ack'.encode("utf-8"), (UDP_IP, UDP_PORT)) # ACK Sender
        fileName, addr = sock.recvfrom(2048)
        sock.sendto('@ack'.encode("utf-8"), (UDP_IP, UDP_PORT)) # ACK Sender
        downloadedFile = open(fileName.decode('utf-8'),'wb')

        while True:
            data, addr = sock.recvfrom(2048)

            if(data != bytes('@ended','utf-8')):
                downloadedFile.write(data)
                sock.sendto('@ack'.encode("utf-8"), (UDP_IP, UDP_PORT)) # ACK Sender

            else:
                break

        data, addr = sock.recvfrom(2048)
        print(data.decode('utf-8'))
        downloadedFile.close()