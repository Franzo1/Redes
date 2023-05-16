from curses.ascii import isdigit
import socket
import random

class socketTCP:

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = None
        self.buffSize = None
        self.message = None
        self.otherAddress = None
        self.otherMessage = None
        self.seq = None

    def set_address(self, address):
        self.address = address

    def set_otherAddress(self, otherAddress):
        self.otherAddress = otherAddress

    def set_buffSize(self, buffSize):
        self.buffSize = buffSize
    
    def set_message(self):
        self.message = input("Escriba su mensaje: ").encode()
    
    def set_seq(self, seq):
        self.seq = seq
    
    def bind(self):
        self.socket.bind(self.address)

    def connect(self, address):
        
        self.seq = random.randint(0, 100)
        dictOne = {
                "[SYN]": "1",
                "[ACK]": "0",
                "[FIN]": "0",
                "[SEQ]": str(self.seq),
                "[DATOS]": ""
        }

        one = socketTCP.create_segment(dictOne)
        print("Cliente: envía SYN")
        self.socket.sendto(one, address)
        recv_message, self.otherAddress = self.socket.recvfrom(20+self.buffSize)
        dictTwo = socketTCP.parse_segment(recv_message)
        
        if(dictTwo["[SYN]"]=="1" and dictTwo["[ACK]"]=="1" and 
           dictTwo["[FIN]"]=="0" and dictTwo["[SEQ]"]==str(self.seq+1)): 
            print("Cliente: recibe SYN+ACK")
            dictThree = {
                "[SYN]": "0",
                "[ACK]": "1",
                "[FIN]": "0",
                "[SEQ]": str(self.seq+2),
                "[DATOS]": ""
            }
            self.set_seq = self.seq + 2
            three = socketTCP.create_segment(dictThree)
            print("Cliente: envía ACK")
            self.socket.sendto(three, self.otherAddress)
            theirIP = self.otherAddress[0]
            Host = self.otherAddress[1]+1
            self.set_otherAddress((theirIP,Host))  

            
    
    def accept(self):

        recv_message, self.otherAddress = self.socket.recvfrom(20+self.buffSize)
        dictOne = socketTCP.parse_segment(recv_message)

        if(dictOne["[SYN]"]=="1" and dictOne["[ACK]"]=="0" and dictOne["[FIN]"]=="0"):
            print("Server: recibe SYN")
            self.set_seq(int(dictOne["[SEQ]"])+1)
            dictTwo = {
                "[SYN]": "1",
                "[ACK]": "1",
                "[FIN]": "0",
                "[SEQ]": str(self.seq),
                "[DATOS]": ""
            }
            
            two = socketTCP.create_segment(dictTwo)
            print("Server: envía SYN+ACK")
            self.socket.sendto(two, self.otherAddress)
            recv_message, self.otherAddress = self.socket.recvfrom(20+self.buffSize)
            dictThree = socketTCP.parse_segment(recv_message)
            
            if(dictThree["[SYN]"]=="0" and dictThree["[ACK]"]=="1" and 
               dictThree["[FIN]"]=="0" and dictThree["[SEQ]"]==str(self.seq+1)):
                print("Server: recibe ACK")
                newSock = socketTCP()
                myIP = self.address[0]
                Host = self.address[1]+1
                newSock.set_address((myIP, Host))
                newSock.set_otherAddress(self.otherAddress)
                newSock.set_buffSize(self.buffSize)
                newSock.set_seq(self.seq+1)
                newSock.bind()
                return newSock, newSock.address

    def send(self):

        print("Cliente: Comienza 3-way handshake")
        byte_inicial = 0

        message_sent_so_far = ''.encode()
        
        firstDict= {
                "[SYN]": "0",
                "[ACK]": "0",
                "[FIN]": "0",
                "[SEQ]": str(self.seq),
                "[DATOS]": str(len(self.message))
            }
        
        firstSegment = socketTCP.create_segment(firstDict)
        self.socket.sendto(firstSegment, self.otherAddress)
        self.socket.settimeout(10)
        
        try:
            recv_message, self.otherAddress = self.socket.recvfrom(20+self.buffSize)
            dictAck = socketTCP.parse_segment(recv_message)
            if (dictAck["[SYN]"]=="0" and dictAck["[ACK]"]=="1" and dictAck["[FIN]"]=="0" and 
                int(dictAck["[SEQ]"])>self.seq and dictAck["[DATOS]"]=="1"):
                print("Cliente: Se enviaron " + str(int(dictAck["[SEQ]"])-self.seq) + " bytes con éxito! (Info len), SEQ = " + str(self.seq))
                self.seq = int(dictAck["[SEQ]"])
        except socket.timeout:
                print("Cliente: Timeout!")
                self.send()
                return

        while True:

            max_byte = min(len(self.message), byte_inicial + self.buffSize)

            message_slice = self.message[byte_inicial: max_byte]
            
            dictSegment = {
                "[SYN]": "0",
                "[ACK]": "0",
                "[FIN]": "0",
                "[SEQ]": str(self.seq),
                "[DATOS]": message_slice.decode()
            }

            segment = socketTCP.create_segment(dictSegment)

            self.socket.sendto(segment, self.otherAddress)

            self.socket.settimeout(10)
            try:
                
                recv_message, self.otherAddress = self.socket.recvfrom(20+self.buffSize)
                dictAck = socketTCP.parse_segment(recv_message)
                
                if (dictAck["[SYN]"]=="0" and dictAck["[ACK]"]=="1" and 
                    dictAck["[FIN]"]=="0" and int(dictAck["[SEQ]"])>self.seq):
                    print("Cliente: Se enviaron " + str(int(dictAck["[SEQ]"])-self.seq) + " bytes con éxito!, SEQ = " + str(self.seq))
                    self.seq = int(dictAck["[SEQ]"])
                
                message_sent_so_far += message_slice

                if max_byte == len(self.message):
                    break

                byte_inicial += self.buffSize

            except socket.timeout:

                print("Cliente: Timeout!")



            
    def recv(self):
        
        print("Server: Comienza 3-way handshake")
        recv_message, self.otherAddress = self.socket.recvfrom(20+self.buffSize)
        dictMessage = socketTCP.parse_segment(recv_message)
        """ if (not isdigit(dictMessage["[DATOS]"])):
            return self.recv() """
        full_message = ""
        backup_message = ""
        bytesSoFar = 0
        message_length = int(dictMessage["[DATOS]"])
        self.set_seq(int(dictMessage["[SEQ]"])+1)
        dictResponse = {
                "[SYN]": "0",
                "[ACK]": "1",
                "[FIN]": "0",
                "[SEQ]": str(self.seq),
                "[DATOS]": "1"
        }
        segmentResponse = socketTCP.create_segment(dictResponse)
        self.socket.sendto(segmentResponse, self.otherAddress)

        is_end_of_message = min(message_length, bytesSoFar) == message_length

        while not is_end_of_message:

            recv_message, self.otherAddress = self.socket.recvfrom(20+self.buffSize)
            dictMessage = socketTCP.parse_segment(recv_message)
            
            if (dictMessage["[SYN]"]=="0" and dictMessage["[ACK]"]=="0" and 
                dictMessage["[FIN]"]=="0" and int(dictMessage["[SEQ]"])==self.seq):
                backup_message += full_message
                print("Server: Se recibió con éxito!, SEQ = " + str(self.seq))
            
            elif (dictMessage["[SYN]"]=="0" and dictMessage["[ACK]"]=="0" and 
                dictMessage["[FIN]"]=="0" and int(dictMessage["[SEQ]"])<self.seq):
                self.set_seq(len(dictMessage["[SEQ]"]))
                full_message = backup_message
                print("Server: Se perdió un mensaje! Volviendo a recibir, SEQ = " + str(self.seq))
            
            full_message += dictMessage["[DATOS]"]
            self.set_seq(self.seq+len(dictMessage["[DATOS]"]))
            
            dictResponse = {
                "[SYN]": "0",
                "[ACK]": "1",
                "[FIN]": "0",
                "[SEQ]": str(self.seq),
                "[DATOS]": ""
            }
            
            segmentResponse = socketTCP.create_segment(dictResponse)
            self.socket.sendto(segmentResponse, self.otherAddress)

            bytesSoFar = len(full_message.encode())
            is_end_of_message = min(message_length, bytesSoFar) == message_length

        self.otherMessage = full_message.encode()
        
        return self.otherMessage, self.otherAddress
    
    @staticmethod
    def parse_segment(segment):
        strSegment = segment.decode()
        listSegment = strSegment.split("|||")
        listKeys = ["[SYN]","[ACK]","[FIN]","[SEQ]","[DATOS]"]
        dictSegment = dict(zip(listKeys,listSegment))
        return dictSegment


    @staticmethod
    def create_segment(dictSegment):
        values = dictSegment.values()
        strSegment = ""
        for i in values:
            strSegment += i + "|||"
        strSegment = strSegment[:-3]
        segment = strSegment.encode()
        return segment