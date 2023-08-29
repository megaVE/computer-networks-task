# Authors:
#
# Guilherme Henrique Pereira Serafini - 2021.1.08.048
# Vinícius Eduardo de Souza Honório - 2021.1.08.024

import socket

TCP_IP = input('Enter IP Address [blank for local]: ')
TCP_PORT = 12000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((TCP_IP, TCP_PORT))

print("TCP Target Port: %s" % TCP_PORT)
print("Client Running: OK")

while True:
	MESSAGE = input()
	sock.send(bytes(MESSAGE, 'utf-8'))
	
	data = sock.recv(1024)

	if(data.decode('utf-8') != '@started'):
		if(not data):
			break
		print(data.decode('utf-8'))
	else: # Receives file from Server.py
		sock.send('@ack'.encode("utf-8")) # ACK Sender
		fileName = sock.recv(1024)
		sock.send('@ack'.encode("utf-8")) # ACK Sender
		downloadedFile = open(fileName.decode('utf-8'),'wb')

		while True:
			data = sock.recv(1024)

			if(data != bytes('@ended','utf-8')):
				downloadedFile.write(data)
				sock.send('@ack'.encode("utf-8")) # ACK Sender

			else:
				break

		data = sock.recv(1024)
		print(data.decode('utf-8'))
		downloadedFile.close()
print("Connection Termated!")
sock.close()