# Authors:
#
# Guilherme Henrique Pereira Serafini - 2021.1.08.048
# Vinícius Eduardo de Souza Honório - 2021.1.08.024

import socket
import os

def parLength(length: int, requiredLength: int): # Paramether checking
    if(length == requiredLength):
        print("Requirement OK")
        return True
    else:
        print("Requirement ERROR")
        if(length < requiredLength):
            errorMsg = 'ERROR: Requirement is lacking paramethers! Expected: %s' % (requiredLength-1)
        else:
            errorMsg = 'ERROR: Requirement is exceeding paramethers! Expected: %s' % (requiredLength-1)
        conn.send(bytes(errorMsg, 'utf-8'))
        return False

def parJoin(parList: list, listType: str, parStr = ''): # Multi-worded paramether
    parList.remove(parList[0])
    for word in parList:
        parStr = " ".join([parStr, word])
        if(parStr[len(parStr)-1] == listType):
            return parStr[2:len(parStr)-1]
    conn.send(bytes('ERROR: Invalid file name!', 'utf-8'))    
    return ''

def changeFolder(currentDir: str, newDir: str, isAbsolute: bool): # Tries changing the current folder address
    if(isAbsolute):
        newCurrentDir = []
    else:
        newCurrentDir = currentDir.split('/')

    for folderDirection in newDir.split('/'):
        if(folderDirection == '.'): # Current folder
            pass

        elif(folderDirection == '..'): # Previous folder
            try:
                newCurrentDir.pop()
            except:
                pass

        else: # Next folder
            newCurrentDir.append(folderDirection)
    
    try: # Attempts new folder address
        os.chdir('/' + '/'.join(newCurrentDir))
        return True
    except:
        os.chdir(currentDir)
        conn.send(bytes('ERROR: "%s" is not a folder and/or cannot be accessed!' % inputData[1],'utf-8'))
        return False

TCP_IP = input('Enter IP Address [blank for local]: ')
TCP_PORT = 12000

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind((TCP_IP, TCP_PORT))
sock.listen(1)

conn, addr = sock.accept()
print("TCP Local Port: %s" % TCP_PORT)
# print('Connection Address: %s' % addr)
print("Server Running: OK")

while True:
    data = conn.recv(1024)
    if(not data):
        break

    print("Client Requirement: %s" % data.decode("utf-8"))

    inputData = data.decode("utf-8").split()
    
    if(inputData[0] == 'ls'):
        if(parLength(len(inputData),1)):
            conn.send(bytes(' | '.join(os.listdir()), 'utf-8'))

    elif(inputData[0] == 'pwd'):
        if(parLength(len(inputData),1)):
            conn.send(bytes(os.getcwd(), 'utf-8'))

    elif(inputData[0] == 'cd'):
        if(inputData[1][0] == "'" or inputData[1][0] == '"'): # General quotes
            inputData[1] = parJoin(inputData.copy(), inputData[1][0])
            inputData = inputData[:2]

        if(parLength(len(inputData),2) and inputData[1] != ''):
            cdSuccess = changeFolder(os.getcwd(), inputData[1], inputData[1][0] == '/')

            if(cdSuccess):
                conn.send(bytes(os.getcwd(), 'utf-8')) 

    elif(inputData[0] == 'scp'):
        if(inputData[1][0] == "'" or inputData[1][0] == '"'): # General quotes
            inputData[1] = parJoin(inputData.copy(), inputData[1][0])
            inputData = inputData[:2]

        if(parLength(len(inputData),2) and inputData[1] != ''):
            currentDir = os.getcwd()
            fileLocation = inputData[1].split('/')
            fileName = fileLocation.pop()
            
            cdSucess = changeFolder(currentDir, '/'.join(fileLocation), inputData[1][0] == '/')

            if(cdSucess and not(fileName in os.listdir())): # Looks for the source file
                conn.send(bytes('ERROR: File "%s" does not exist!' % fileName, 'utf-8'))    
            elif(cdSucess): # Opens the file
                try:
                    fd = os.open(fileName, os.O_RDONLY) # os.O_BINARY
                    sourceFile = os.fdopen(fd, 'rb', 1024)
                except:
                    conn.send(bytes('ERROR: File "%s" cannot be accessed!' % fileName, 'utf-8'))
                
                if(sourceFile): # Reads the file
                    conn.send(bytes('@started', 'utf-8'))
                    data = conn.recv(1024) # ACK Receiver
                    conn.send(bytes(fileName, 'utf-8'))
                    data = conn.recv(1024) # ACK Receiver
                    try:
                        fileContent = os.read(fd, 1024)
                        while(fileContent): # Sends the file
                            conn.send(fileContent)
                            data = conn.recv(1024) # ACK Receiver
                            fileContent = os.read(fd, 1024)
                        returnStatus = 'File "%s" Download OK!' % fileName
                    except:
                        returnStatus = 'File "%s" Download ERROR!' % fileName
                    finally:
                        sourceFile.close()
                        conn.send(bytes('@ended', 'utf-8'))
                        conn.send(bytes(returnStatus, 'utf-8'))

            os.chdir(currentDir)

    else:
        conn.send(bytes('ERROR: Requirement "%s" is not valid!' % inputData[0], 'utf-8'))
print("Connection Termated!")
conn.close()
