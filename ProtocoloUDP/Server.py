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
        sock.sendto(bytes(errorMsg, 'utf-8'), addr)
        return False

def parJoin(parList: list, listType: str, parStr = ''): # Multi-worded paramether
    parList.remove(parList[0])
    for word in parList:
        parStr = " ".join([parStr, word])
        if(parStr[len(parStr)-1] == listType):
            return parStr[2:len(parStr)-1]
    sock.sendto(bytes('ERROR: Invalid file name!', 'utf-8'), addr)    
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
        sock.sendto(bytes('ERROR: "%s" is not a folder and/or cannot be accessed!' % inputData[1],'utf-8'),addr)
        return False

UDP_IP = input('Enter IP Address [blank for local]: ')
UDP_PORT = 12000

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Internet|UDP
sock.bind(('', UDP_PORT))

print("UDP Local Port: %s" % UDP_PORT)
print("Server Running: OK")

while True:
    data, addr = sock.recvfrom(2048)
    print("Client Requirement: %s" % data.decode("utf-8"))

    inputData = data.decode("utf-8").split()

    if(inputData[0] == 'ls'):
        if(parLength(len(inputData),1)):
            sock.sendto(bytes(' | '.join(os.listdir()), 'utf-8'), addr)

    elif(inputData[0] == 'pwd'):
        if(parLength(len(inputData),1)):
            sock.sendto(bytes(os.getcwd(), 'utf-8'), addr)

    elif(inputData[0] == 'cd'):
        if(inputData[1][0] == "'" or inputData[1][0] == '"'): # General quotes
            inputData[1] = parJoin(inputData.copy(), inputData[1][0])
            inputData = inputData[:2]

        if(parLength(len(inputData),2) and inputData[1] != ''):
            cdSuccess = changeFolder(os.getcwd(), inputData[1], inputData[1][0] == '/')

            if(cdSuccess):
                sock.sendto(bytes(os.getcwd(), 'utf-8'), addr) 

    elif(inputData[0] == 'scp'):
        if(inputData[1][0] == "'" or inputData[1][0] == '"'): # Treats mult-worded paramethers
            inputData[1] = parJoin(inputData.copy(), inputData[1][0])
            inputData = inputData[:2]

        if(parLength(len(inputData),2) and inputData[1] != ''):
            currentDir = os.getcwd()
            fileLocation = inputData[1].split('/')
            fileName = fileLocation.pop()
            
            cdSucess = changeFolder(currentDir, '/'.join(fileLocation), inputData[1][0] == '/')

            if(cdSucess and not(fileName in os.listdir())): # Looks for the source file
                sock.sendto(bytes('ERROR: File "%s" does not exist!' % fileName, 'utf-8'), addr)    
            elif(cdSucess): # Opens the file
                try:
                    fd = os.open(fileName, os.O_RDONLY) # os.O_BINARY
                    sourceFile = os.fdopen(fd, 'rb', 2048)
                except:
                    sock.sendto(bytes('ERROR: File "%s" cannot be accessed!' % fileName, 'utf-8'), addr)
                
                if(sourceFile): # Reads the file
                    sock.sendto(bytes('@started', 'utf-8'), addr)
                    data, addr = sock.recvfrom(2048) # ACK Receiver
                    sock.sendto(bytes(fileName, 'utf-8'), addr)
                    data, addr = sock.recvfrom(2048) # ACK Receiver
                    try:
                        fileContent = os.read(fd, 2048)
                        while(fileContent): # Sends the file
                            sock.sendto(fileContent, addr)
                            data, addr = sock.recvfrom(2048) # ACK Receiver
                            fileContent = os.read(fd, 2048)
                        returnStatus = 'File "%s" Download OK!' % fileName
                    except:
                        returnStatus = 'File "%s" Download ERROR!' % fileName
                    finally:
                        sourceFile.close()
                        sock.sendto(bytes('@ended', 'utf-8'), addr)
                        sock.sendto(bytes(returnStatus, 'utf-8'), addr)

            os.chdir(currentDir)

    else:
        sock.sendto(bytes('ERROR: Requirement "%s" is not valid!' % inputData[0], 'utf-8'), addr)