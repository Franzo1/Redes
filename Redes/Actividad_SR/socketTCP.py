from curses.ascii import isdigit
import socket
import textwrap
import random
import timerList as tm
import slidingWindow as sw

class socketTCP:

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = None
        self.buffSize = None
        self.message = None
        self.otherAddress = None
        self.otherMessage = None
        self.otherMessageLen = None
        self.bytesSoFar = None
        self.seq = None
        self.timeout = None

    def set_address(self, address):
        self.address = address

    def set_otherAddress(self, otherAddress):
        self.otherAddress = otherAddress

    def set_buffSize(self, buffSize):
        self.buffSize = buffSize
    
    def set_message(self):
        self.message = input("Escriba su mensaje: ").encode()

    def set_otherMessage(self, otherMessage):
        self.otherMessage = otherMessage

    def set_otherMessageLen(self, otherMessageLen):
        self.otherMessageLen = otherMessageLen
    
    def set_bytesSoFar(self, bytesSoFar):
        self.bytesSoFar = bytesSoFar

    def set_seq(self, seq):
        self.seq = seq
    
    def set_timeout(self, timeout):
        self.timeout = timeout

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
        self.socket.settimeout(10)
        
        try:
            recv_message, self.otherAddress = self.socket.recvfrom(23)
            dictTwo = socketTCP.parse_segment(recv_message)
            
            if(dictTwo["[SYN]"]=="1" and dictTwo["[ACK]"]=="1" and 
            dictTwo["[FIN]"]=="0"): 
                print("Cliente: recibe SYN+ACK")
                dictThree = {
                    "[SYN]": "0",
                    "[ACK]": "1",
                    "[FIN]": "0",
                    "[SEQ]": str(self.seq+2),
                    "[DATOS]": ""
                }
                self.set_seq(self.seq + 2)
                three = socketTCP.create_segment(dictThree)
                print("Cliente: envía ACK")
                self.socket.sendto(three, self.otherAddress)
                theirIP = self.otherAddress[0]
                Host = self.otherAddress[1]+1
                self.set_otherAddress((theirIP,Host))  
            else:
                print("Cliente: SYN+ACK llegó con pérdidas!")
                self.connect(address)
        
        except socket.timeout:
            print("Cliente: Timeout!")
            self.connect(address)
            
    
    def accept(self):

        recv_message, self.otherAddress = self.socket.recvfrom(23)
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
            nTimeouts = 0
            
            while nTimeouts < 6:
                self.socket.settimeout(5)
                try:
                    recv_message, self.otherAddress = self.socket.recvfrom(23)
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
                    
                    elif(dictThree["[SYN]"]=="1" and dictThree["[ACK]"]=="0" and dictThree["[FIN]"]=="0"):
                        print("Server: Volviendo a recibir SYN")
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
                
                except socket.timeout:
                    nTimeouts += 1

            print("Server: el cliente ya comenzó Stop and Wait!")
            newSock = socketTCP()
            myIP = self.address[0]
            Host = self.address[1]+1
            newSock.set_address((myIP, Host))
            newSock.set_otherAddress(self.otherAddress)
            newSock.set_buffSize(self.buffSize)
            newSock.set_seq(self.seq+1)
            newSock.bind()
            return newSock, newSock.address

        else:
            print("Server: SYN llegó con perdidas!")
            self.accept()

    def send_using_stop_and_wait(self):

        print("Cliente: Comienza Stop and Wait")
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
            recv_message, self.otherAddress = self.socket.recvfrom(23)
            dictAck = socketTCP.parse_segment(recv_message)
            if (dictAck["[SYN]"]=="0" and dictAck["[ACK]"]=="1" and dictAck["[FIN]"]=="0" and 
                int(dictAck["[SEQ]"])>self.seq and dictAck["[DATOS]"]=="1"):
                print("Cliente: Se enviaron " + str(int(dictAck["[SEQ]"])-self.seq) + " bytes con éxito! (Info len), SEQ = " + str(self.seq))
                self.seq = int(dictAck["[SEQ]"])
            else:
                print("Cliente: Mensaje llegó mal del server!")
                self.send_using_stop_and_wait()
                return
        except socket.timeout:
                print("Cliente: Timeout!")
                self.send_using_stop_and_wait()
                return

        finalAttempts = 0
        while True:
            if finalAttempts == 5:
                print("Cliente: El server ya debe tener el mensaje completo")
                break

            max_byte = min(len(self.message), byte_inicial + 3)

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
                
                recv_message, self.otherAddress = self.socket.recvfrom(23)
                dictAck = socketTCP.parse_segment(recv_message)
                
                if (dictAck["[SYN]"]=="0" and dictAck["[ACK]"]=="1" and 
                    dictAck["[FIN]"]=="0" and int(dictAck["[SEQ]"])>self.seq):
                    print("Cliente: Se enviaron " + str(int(dictAck["[SEQ]"])-self.seq) + " bytes con éxito!, SEQ = " + str(self.seq))
                    self.seq = int(dictAck["[SEQ]"])
                
                    message_sent_so_far += message_slice

                    if max_byte == len(self.message):
                        break

                    byte_inicial += 3
                else:
                    print("Cliente: Mensaje llegó mal del server!")

            except socket.timeout:

                print("Cliente: Timeout!")
                if max_byte == len(self.message):
                    finalAttempts += 1



            
    def recv_using_stop_and_wait(self):
        
        print("Server: Comienza Stop and Wait")
        recv_message, self.otherAddress = self.socket.recvfrom(23)
        dictMessage = socketTCP.parse_segment(recv_message)
        while True:
            if (dictMessage["[SYN]"]=="0" and dictMessage["[ACK]"]=="0" and 
                    dictMessage["[FIN]"]=="0" and dictMessage["[DATOS]"].isnumeric()):
                print("Server: Se recibió el largo del mensaje!")
                full_message = ""
                backup_message = ""
                bytesSoFar = 0
                self.set_bytesSoFar(0)
                message_length = int(dictMessage["[DATOS]"])
                self.set_otherMessageLen(message_length)
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
                isSegment = False

                is_end_of_message = min(message_length, bytesSoFar) == message_length

                firstMessage = True
                recv_message, self.otherAddress = self.socket.recvfrom(23)
                dictMessage = socketTCP.parse_segment(recv_message)
                if (not (dictMessage["[SYN]"]=="0" and dictMessage["[ACK]"]=="0" and 
                    dictMessage["[FIN]"]=="0" and int(dictMessage["[SEQ]"])==self.seq)):
                    print("Server: El cliente no recibió confirmación!")
                    self.set_seq(self.seq-1)
                    self.recv_using_stop_and_wait()
                    return
                break
            elif (dictMessage["[SYN]"]=="0" and dictMessage["[ACK]"]=="0" and 
                    dictMessage["[FIN]"]=="0"):
                full_message = ""
                backup_message = ""
                bytesSoFar = 0
                message_length = self.otherMessageLen - self.bytesSoFar
                is_end_of_message = min(message_length, bytesSoFar) == message_length
                firstMessage = True
                recv_message, self.otherAddress = self.socket.recvfrom(23)
                dictMessage = socketTCP.parse_segment(recv_message)
                break
            else:
                print("Server: No llegó bien el largo del mensaje!")
                self.recv_using_stop_and_wait()
                return          

        while not is_end_of_message:

            if(not firstMessage):
                recv_message, self.otherAddress = self.socket.recvfrom(23)
                dictMessage = socketTCP.parse_segment(recv_message)
            firstMessage=False
            
            if (dictMessage["[SYN]"]=="0" and dictMessage["[ACK]"]=="0" and 
                dictMessage["[FIN]"]=="0" and int(dictMessage["[SEQ]"])==self.seq):
                backup_message = full_message
                isSegment = True
                print("Server: Se recibió con éxito!, SEQ = " + str(self.seq))
            
            elif (dictMessage["[SYN]"]=="0" and dictMessage["[ACK]"]=="0" and 
                dictMessage["[FIN]"]=="0" and int(dictMessage["[SEQ]"])<self.seq):
                self.set_seq(int(dictMessage["[SEQ]"]))
                full_message = backup_message
                bytesSoFar -= len(dictMessage["[DATOS]"])
                isSegment = True
                print("Server: Se perdió un mensaje! Volviendo a recibir, SEQ = " + str(self.seq))
            
            else:
                isSegment = False

            if isSegment:
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

                bytesSoFar += len(dictMessage["[DATOS]"])
                is_end_of_message = min(message_length, bytesSoFar) == message_length
                if (bytesSoFar > self.buffSize):
                    self.set_bytesSoFar(self.bytesSoFar+bytesSoFar)
                    break

        self.set_otherMessage(full_message.encode())
        
        return self.otherMessage, self.otherAddress
    
    def close(self,t=0):

        if (t==3):
            self.socket.close()
            print("Cliente: conexión cerrada")
            return

        dictOne = {
                "[SYN]": "0",
                "[ACK]": "0",
                "[FIN]": "1",
                "[SEQ]": str(self.seq),
                "[DATOS]": ""
        }

        one = socketTCP.create_segment(dictOne)
        print("Cliente: envía FIN")
        self.socket.sendto(one, self.otherAddress)
        self.socket.settimeout(10)
        
        try:
            recv_message, self.otherAddress = self.socket.recvfrom(23)
            dictTwo = socketTCP.parse_segment(recv_message)
            
            if(dictTwo["[SYN]"]=="0" and dictTwo["[ACK]"]=="1" and 
            dictTwo["[FIN]"]=="1" and dictTwo["[SEQ]"]==str(self.seq+1)): 
                print("Cliente: recibe FIN+ACK")
                dictThree = {
                    "[SYN]": "0",
                    "[ACK]": "1",
                    "[FIN]": "0",
                    "[SEQ]": str(self.seq+2),
                    "[DATOS]": ""
                }
                self.set_seq = self.seq + 2
                three = socketTCP.create_segment(dictThree)
                print("Cliente: envía ACK (1)")
                finalTimeout = 0
                self.socket.sendto(three, self.otherAddress)

                while True:
                    self.socket.settimeout(10)
                    try:
                        recv_message, self.otherAddress = self.socket.recvfrom(23)
                    except socket.timeout:
                        finalTimeout += 1
                        if (finalTimeout == 3):
                            break
                        self.socket.sendto(three, self.otherAddress)
                        print("Cliente: envía ACK ("+str(finalTimeout+1)+")")
                
                self.socket.close()
                print("Cliente: conexión cerrada")

            else:
                print("Cliente: SYN+ACK llegó con pérdidas!")
                self.close(t)
        
        except socket.timeout:
            print("Cliente: Timeout!")
            t+=1
            self.close(t)

    def recv_close(self):

        recv_message, self.otherAddress = self.socket.recvfrom(23)
        dictOne = socketTCP.parse_segment(recv_message)

        if(dictOne["[SYN]"]=="0" and dictOne["[ACK]"]=="0" and dictOne["[FIN]"]=="1"):
            print("Server: recibe FIN")
            self.set_seq(int(dictOne["[SEQ]"])+1)
            dictTwo = {
                "[SYN]": "0",
                "[ACK]": "1",
                "[FIN]": "1",
                "[SEQ]": str(self.seq),
                "[DATOS]": ""
            }
            
            two = socketTCP.create_segment(dictTwo)
            print("Server: envía FIN+ACK")
            self.socket.sendto(two, self.otherAddress)
            finalTimeout = 0
            
            while finalTimeout < 3:
                self.socket.settimeout(10)
                try:
                    recv_message, self.otherAddress = self.socket.recvfrom(20+self.buffSize)
                    dictThree = socketTCP.parse_segment(recv_message)
                    
                    if(dictThree["[SYN]"]=="0" and dictThree["[ACK]"]=="1" and 
                    dictThree["[FIN]"]=="0" and dictThree["[SEQ]"]==str(self.seq+1)):
                        print("Server: recibe ACK")
                        self.set_seq(int(dictThree["[SEQ]"]))
                        break
                    
                    elif(dictThree["[SYN]"]=="0" and dictThree["[ACK]"]=="0" and 
                        dictThree["[FIN]"]=="1" and dictThree["[SEQ]"]==str(self.seq-1)):
                        print("Server: Volviendo a recibir FIN")
                        dictTwo = {
                            "[SYN]": "0",
                            "[ACK]": "1",
                            "[FIN]": "1",
                            "[SEQ]": str(self.seq),
                            "[DATOS]": ""
                        }           
                        two = socketTCP.create_segment(dictTwo)
                        print("Server: envía FIN+ACK")
                        self.socket.sendto(two, self.otherAddress)

                except socket.timeout:
                    finalTimeout += 1
            
            self.socket.close()
            print("Server: conexión cerrada")

        else:
            print("Server: FIN llegó con perdidas!")
            self.recv_close()

    def send(self, mode="stop_and_wait"):
        self.set_message()
        if mode == "stop_and_wait":
            self.send_using_stop_and_wait()
        if mode == "selective_repeat":
            self.send_using_selective_repeat()
    
    def recv(self, buff_size, mode="stop_and_wait"):
        self.set_buffSize(buff_size)
        if mode == "stop_and_wait":
            self.recv_using_stop_and_wait()
        if mode == "selective_repeat":
            self.recv_using_selective_repeat()

    def send_using_selective_repeat(self):

        print("Cliente: Comienza Selective Repeat!")

        seqY = self.seq
        
        message_length = len(self.message)
        message = self.message.decode()
        n = 16
        i = 0
        # bytesSoFar = 0
        chunks = [message[i:i+n] for i in range(0, len(message), n)]
        """ chunk_portion = ""
        
        while True:
            chunk_portion += str(encoded_message[i]).decode()
            bytesSoFar += len(encoded_message[i])
            if(bytesSoFar >= n):
                n += 16
                chunks += chunk_portion
                chunk_portion = ""
            i+=1
            if bytesSoFar >= message_length:
                break """           

        data_list = [str(message_length)]+chunks
        
        window_size = 3
        data_window = sw.SlidingWindow(window_size, data_list, seqY)
        acks = [0] * window_size*2
        seqs = [0] * window_size
        window_moves = 0
        
        timeout_list = tm.TimerList(self.timeout, window_size)

        self.socket.setblocking(False)
        
        for i in range(window_size):
            current_data = data_window.get_data(i)
            seqs[i] = data_window.get_sequence_number(i)
            dictSegment = {
                            "[SYN]": "0",
                            "[ACK]": "0",
                            "[FIN]": "0",
                            "[SEQ]": str(seqs[i]),
                            "[DATOS]": str(current_data)
            }
            current_segment = socketTCP.create_segment(dictSegment)
            self.socket.sendto(current_segment, self.otherAddress)
            print("Cliente: Se envió el trozo de SEQ = "+str(seqs[i]))
            print(current_data)
            timeout_list.start_timer((seqs[i]-seqY)%window_size)

        while True:
            try:
                timeouts = timeout_list.get_timed_out_timers()
                if len(timeouts) > 0:
                    print("Holi")
                    displace = 0
                    for i in range(window_size):
                        seq_num = data_window.get_sequence_number(i)
                        if seq_num != None:
                            if seq_num-seqY > window_size-1:
                                displace += 1
                    for i in timeouts:
                        current_data = data_window.get_data((i+displace)%window_size)
                        current_seq = data_window.get_sequence_number((i+displace)&window_size)
                        dictSegment = {
                            "[SYN]": "0",
                            "[ACK]": "0",
                            "[FIN]": "0",
                            "[SEQ]": str(current_seq),
                            "[DATOS]": str(current_data)
                        }
                        current_segment = socketTCP.create_segment(dictSegment)
                        self.socket.sendto(current_segment, self.otherAddress)
                        print("Cliente: Se volvió a enviar el trozo de SEQ = "+str(current_seq))
                        timeout_list.start_timer((current_seq - seqY)%window_size)
                answer, address = self.socket.recvfrom(self.buffSize+20)   
            except BlockingIOError:
                continue
            else:
                answerDict = socketTCP.parse_segment(answer)
                if(answerDict["[SYN]"]=="0" and answerDict["[ACK]"]=="1" and 
                    answerDict["[FIN]"]=="0" and seqY <= int(answerDict["[SEQ]"]) <= seqY + 2*window_size - 1):
                    aSeq = int(answerDict["[SEQ]"])
                    index = (aSeq - seqY) % window_size
                    timeout_list.stop_timer(index)
                    acks[aSeq - seqY] = 1
                    if seqs.index(aSeq) == 0:
                        for i in range(window_size*2):
                            if acks[(i+(aSeq-seqY))%(window_size*2)] == 1:
                                acks[(i+(aSeq-seqY))%(window_size*2)] = 0
                                data_window.move_window(1)
                                window_moves+=1
                                if window_moves == len(data_list):
                                    return
                                current_data = data_window.get_data(window_size-1)
                                if current_data != None:
                                    seqs[(i+(aSeq-seqY))%window_size] = data_window.get_sequence_number(window_size-1)
                                    dictSegment = {
                                                    "[SYN]": "0",
                                                    "[ACK]": "0",
                                                    "[FIN]": "0",
                                                    "[SEQ]": str(seqs[(i+(aSeq-seqY))%window_size]),
                                                    "[DATOS]": str(current_data)
                                    }
                                    current_segment = socketTCP.create_segment(dictSegment)
                                    self.socket.sendto(current_segment, self.otherAddress)
                                    print("Cliente: Se envió el trozo de SEQ = "+str(seqs[(i+(aSeq-seqY))%window_size]))
                                    timeout_list.start_timer((i+(aSeq-seqY))%window_size)
                            else:
                                break

    def recv_using_selective_repeat(self):

        print("Server: Comienza Selective Repeat!")
        print(self.otherAddress)

        window_size = 3
        seqY = self.seq
        firstSeq = seqY
        recv_window = sw.SlidingWindow(window_size, [], seqY)
        message_length = 0
        received = [0] * window_size*2
        seqs = [0] * window_size
        buff_size = self.buffSize
        bytesSoFar = 0
        messageSoFar = ""

        while True:
            message, address = self.socket.recvfrom(self.buffSize+20)
            dictMessage = socketTCP.parse_segment(message)
            for i in range(window_size):
                seqs[i] = ((firstSeq-seqY+i)%(window_size*2))+seqY

            if(dictMessage["[SYN]"]=="0" and dictMessage["[ACK]"]=="0" and dictMessage["[FIN]"]=="0" 
               and dictMessage["[SEQ]"].isnumeric() and dictMessage["[DATOS]"]!=""):
                print(seqs)
                if message_length == 0 and int(dictMessage["[SEQ]"]) == seqY:
                    print("Server: Se recibió el largo del mensaje!")
                    message_length = int(dictMessage["[DATOS]"])
                    received[0] = 1
                    recv_window.put_data(dictMessage["[DATOS]"], int(dictMessage["[SEQ]"]), 0)
                    dictAck = {
                        "[SYN]": "0",
                        "[ACK]": "1",
                        "[FIN]": "0",
                        "[SEQ]": dictMessage["[SEQ]"],
                        "[DATOS]": ""
                    }
                    ack_segment = socketTCP.create_segment(dictAck)
                    self.socket.sendto(ack_segment, self.otherAddress)
                    next_seq = recv_window.get_sequence_number(0)
                    while True:
                        if received[next_seq - seqY] == 1:
                            current_seq = recv_window.get_sequence_number(0)
                            received[current_seq - seqY] = 0
                            if not (next_seq == seqY and messageSoFar == ""):
                                messageSoFar += recv_window.get_data(0)
                            recv_window.move_window(1)
                            firstSeq = ((firstSeq-seqY+1)%(window_size*2))+seqY
                            next_seq = ((current_seq-seqY+1)%(window_size*2))+seqY
                            print("Server: se ha movido la ventana")
                            seqs[(next_seq - seqY) % window_size] = (next_seq + window_size)%(window_size*2)
                        else:
                            break
                elif seqs.count(int(dictMessage["[SEQ]"])) == 0:
                    dictAck = {
                        "[SYN]": "0",
                        "[ACK]": "1",
                        "[FIN]": "0",
                        "[SEQ]": dictMessage["[SEQ]"],
                        "[DATOS]": ""
                    }
                    ack_segment = socketTCP.create_segment(dictAck)
                    self.socket.sendto(ack_segment, self.otherAddress)
                elif seqs.count(int(dictMessage["[SEQ]"])) > 0:
                    print("Server: Se recibió un segmento de SEQ = " + dictMessage["[SEQ]"])
                    print(len(dictMessage["[DATOS]"].encode()))
                    bytesSoFar += len(dictMessage["[DATOS]"].encode())
                    for i in range(window_size):
                        if int(dictMessage["[SEQ]"]) == ((firstSeq-seqY+i)%(window_size*2))+seqY:
                            window_index = i
                            break
                    recv_window.put_data(dictMessage["[DATOS]"], int(dictMessage["[SEQ]"]), window_index)
                    dictAck = {
                        "[SYN]": "0",
                        "[ACK]": "1",
                        "[FIN]": "0",
                        "[SEQ]": dictMessage["[SEQ]"],
                        "[DATOS]": ""
                    }
                    ack_segment = socketTCP.create_segment(dictAck)
                    self.socket.sendto(ack_segment, self.otherAddress)
                    received[int(dictMessage["[SEQ]"])-seqY] = 1
                    next_seq = int(dictMessage["[SEQ]"])
                    if window_index == 0:
                        while True:
                            if received[next_seq - seqY] == 1:
                                current_seq = recv_window.get_sequence_number(0)
                                received[current_seq - seqY] = 0
                                messageSoFar += recv_window.get_data(0)
                                recv_window.move_window(1)
                                firstSeq = ((firstSeq-seqY+1)%(window_size*2))+seqY
                                next_seq = ((current_seq-seqY+1)%(window_size*2))+seqY
                                print("Server: se ha movido la ventana")
                                seqs[(next_seq - seqY) % window_size] = (next_seq + window_size)%(window_size*2)
                            else:
                                break
                    if bytesSoFar >= min(message_length, buff_size):
                        print(self.otherAddress)
                        self.set_otherMessage(messageSoFar)
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