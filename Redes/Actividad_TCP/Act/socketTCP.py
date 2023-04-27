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
        recv_message, self.otherAddress = self.socket.recvfrom(self.buffSize)
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

        recv_message, self.otherAddress = self.socket.recvfrom(self.buffSize)
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
            recv_message, self.otherAddress = self.socket.recvfrom(self.buffSize)
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
                return newSock, newSock.address

    def send_in_bytes(self):

        byte_inicial = 0

        message_sent_so_far = ''.encode()

        while True:

            max_byte = min(len(self.message), byte_inicial + self.buffSize)

            message_slice = self.message[byte_inicial: max_byte]
            
            dictSegment = {
                "[SYN]": "0",
                "[ACK]": "0",
                "[FIN]": "0",
                "[SEQ]": "8",
                "[DATOS]": message_slice.decode()
            }

            segment = socketTCP.create_segment(dictSegment)

            self.socket.sendto(segment, self.otherAddress)

            message_sent_so_far += message_slice

            if max_byte == len(self.message):
                self.socket.sendto("stop".encode(), self.otherAddress)
                break

            byte_inicial += self.buffSize

    def receive_in_bytes(self):
    
        recv_message, self.otherAddress = self.socket.recvfrom(self.buffSize)
        full_message = recv_message

        is_end_of_message = recv_message == "stop".encode()

        while not is_end_of_message:

            recv_message, self.otherAddress = self.socket.recvfrom(self.buffSize)

            full_message += recv_message

            is_end_of_message = recv_message == "stop".encode()

        index = full_message.rfind("stop".encode())
        full_message = full_message[:index]

        self.otherMessage = full_message.decode()
        
        return full_message, self.otherAddress
    
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