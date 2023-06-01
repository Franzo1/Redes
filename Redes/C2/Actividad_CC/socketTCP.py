from curses.ascii import isdigit
import socket
import textwrap
import random
import timerList as tm
import slidingWindow as sw
import slidingWindowCC as swcc

class socketTCP:

    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.address = None
        self.buffSize = None
        self.message = None
        self.otherAddress = None
        self.otherMessage = "".encode()
        self.otherMessageLen = None
        self.bytesSoFar = None
        self.seq = None
        self.lastSeq = None
        self.timeout = None
        self.messageIsComplete = True
        self.number_of_sent_segments = 0
        self.window_size = 0
        self.expected_seq = None
        self.last_ack = None

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

    def set_lastSeq(self, lastSeq):
        self.lastSeq = lastSeq
    
    def set_timeout(self, timeout):
        self.timeout = timeout
    
    def set_messageIsComplete(self, messageIsComplete):
        self.messageIsComplete = messageIsComplete
    
    def set_number_of_sent_segments(self, number_of_sent_segments):
        self.number_of_sent_segments = number_of_sent_segments

    def set_window_size(self, window_size):
        self.window_size = window_size

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
                        newSock.set_seq(int(dictTwo["[SEQ]"])+1)
                        newSock.bind()
                        return newSock, newSock.address
                    
                    elif(dictThree["[SYN]"]=="1" and dictThree["[ACK]"]=="0" and dictThree["[FIN]"]=="0"):
                        print("Server: Volviendo a recibir SYN")
                        self.set_seq(int(dictThree["[SEQ]"])+1)
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

            print("Server: el cliente ya comenzó!")
            newSock = socketTCP()
            myIP = self.address[0]
            Host = self.address[1]+1
            newSock.set_address((myIP, Host))
            newSock.set_otherAddress(self.otherAddress)
            newSock.set_buffSize(self.buffSize)
            newSock.set_seq(int(dictTwo["[SEQ]"])+1)
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
        self.set_number_of_sent_segments(self.number_of_sent_segments+1)
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
        
        while True:

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
            self.set_number_of_sent_segments(self.number_of_sent_segments+1)
            self.socket.sendto(segment, self.otherAddress)

            self.socket.settimeout(10)
            try:
                
                recv_message, self.otherAddress = self.socket.recvfrom(23)
                dictAck = socketTCP.parse_segment(recv_message)
                
                if (dictAck["[SYN]"]=="0" and dictAck["[ACK]"]=="1" and 
                    dictAck["[FIN]"]=="0" and int(dictAck["[SEQ]"])>=self.seq):
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
                    dictMessage["[FIN]"]=="0" and int(dictMessage["[SEQ]"])==self.seq):
                full_message = ""
                backup_message = ""
                bytesSoFar = 0
                message_length = self.otherMessageLen - self.bytesSoFar
                is_end_of_message = min(message_length, bytesSoFar) == message_length
                firstMessage = True
                recv_message, self.otherAddress = self.socket.recvfrom(23)
                dictMessage = socketTCP.parse_segment(recv_message)
                break
            elif (dictMessage["[SYN]"]=="0" and dictMessage["[ACK]"]=="0" and 
                    dictMessage["[FIN]"]=="0" and int(dictMessage["[SEQ]"])<self.seq):
                print("Server: Cliente está atrapado en el Stop and Wait anterior!")
                dictAck = {
                    "[SYN]": "0",
                    "[ACK]": "1",
                    "[FIN]": "0",
                    "[SEQ]": dictMessage["[SEQ]"],
                    "[DATOS]": ""
                }
                ack_segment = socketTCP.create_segment(dictAck)
                self.socket.sendto(ack_segment, self.otherAddress)
                self.recv_using_stop_and_wait()
                return          
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

        print("Cliente: comienza el cierre de conexión")

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

        print("Server: comienza el cierre de conexión")

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
        elif (dictOne["[SYN]"]=="0" and dictOne["[ACK]"]=="0" and dictOne["[FIN]"]=="0"):
            print("Server: Cliente está atrapado en el Stop and Wait anterior!")
            dictAck = {
                "[SYN]": "0",
                "[ACK]": "1",
                "[FIN]": "0",
                "[SEQ]": dictOne["[SEQ]"],
                "[DATOS]": ""
            }
            ack_segment = socketTCP.create_segment(dictAck)
            self.socket.sendto(ack_segment, self.otherAddress)
            self.recv_close()
        else:
            print("Server: FIN llegó con perdidas!")
            self.recv_close()

    def send(self, mode="stop_and_wait"):
        self.set_message()
        if mode == "stop_and_wait":
            self.send_using_stop_and_wait()
        if mode == "selective_repeat":
            self.send_using_selective_repeat()
        seg_sent = self.number_of_sent_segments
        self.set_number_of_sent_segments(0)
        print("Cliente: Finalizó el envío del mensaje (Número de segmentos enviados: "+str(seg_sent)+")")
    
    def recv(self, buff_size, mode="stop_and_wait"):
        self.set_buffSize(buff_size)
        if mode == "stop_and_wait":
            return self.recv_using_stop_and_wait()
        if mode == "selective_repeat":
            return self.recv_using_selective_repeat()

    def send_using_selective_repeat(self):

        print("Cliente: Comienza Selective Repeat!")

        seqY = self.seq
        
        message_length = len(self.message)
        message = self.message.decode()
        n = 4
        i = 0
        chunks = [message[i:i+n] for i in range(0, len(message), n)]   

        data_list = [str(message_length)]+chunks
        
        window_size = self.window_size
        data_window = sw.SlidingWindow(window_size, data_list, seqY)
        acks = [0] * window_size*2
        seqs = [0] * window_size
        window_moves = 0
        
        timeout_list = tm.TimerList(self.timeout, window_size)

        self.socket.setblocking(False)
        
        for i in range(window_size):
            current_data = data_window.get_data(i)
            seqs[i] = data_window.get_sequence_number(i)
            if seqs[i] != None:
                dictSegment = {
                                "[SYN]": "0",
                                "[ACK]": "0",
                                "[FIN]": "0",
                                "[SEQ]": str(seqs[i]),
                                "[DATOS]": str(current_data)
                }
                current_segment = socketTCP.create_segment(dictSegment)
                self.set_number_of_sent_segments(self.number_of_sent_segments+1)
                self.socket.sendto(current_segment, self.otherAddress)
                print("Cliente: Se envió el trozo de SEQ = "+str(seqs[i]))
                timeout_list.start_timer((seqs[i]-seqY)%window_size)

        while True:
            try:
                timeouts = timeout_list.get_timed_out_timers()
                if len(timeouts) > 0:
                    nones = 0
                    for i in range(window_size):
                        seq_num = data_window.get_sequence_number(i)
                        if seq_num == None:
                            nones += 1
                    for i in timeouts:
                        for x in range(0, window_size-nones):
                            if i == (data_window.get_sequence_number(x)-seqY)%window_size:
                                windex = x
                                break
                        current_data = data_window.get_data(windex)
                        current_seq = data_window.get_sequence_number(windex)
                        dictSegment = {
                            "[SYN]": "0",
                            "[ACK]": "0",
                            "[FIN]": "0",
                            "[SEQ]": str(current_seq),
                            "[DATOS]": str(current_data)
                        }
                        current_segment = socketTCP.create_segment(dictSegment)
                        self.set_number_of_sent_segments(self.number_of_sent_segments+1)
                        self.socket.sendto(current_segment, self.otherAddress)

                        print("Cliente: Se volvió a enviar el trozo de SEQ = "+str(current_seq))
                        timeout_list.start_timer((current_seq - seqY)%window_size)
                timeouts = []
                answer, address = self.socket.recvfrom(self.buffSize+20)   
            except BlockingIOError:
                continue
            else:
                answerDict = socketTCP.parse_segment(answer)
                if(answerDict["[SYN]"]=="0" and answerDict["[ACK]"]=="1" and 
                    answerDict["[FIN]"]=="0" and seqY <= int(answerDict["[SEQ]"]) <= seqY + 2*window_size - 1):
                    print("Cliente: Se recibió ACK para SEQ = " + answerDict["[SEQ]"])
                    aSeq = int(answerDict["[SEQ]"])
                    index = (aSeq - seqY) % window_size
                    timeout_list.stop_timer(index)
                    acks[aSeq - seqY] = 1
                    if data_window.get_sequence_number(0) == aSeq:
                        for i in range(window_size*2):
                            if acks[(i+(aSeq-seqY))%(window_size*2)] == 1:
                                acks[(i+(aSeq-seqY))%(window_size*2)] = 0
                                data_window.move_window(1)
                                print("Cliente: Se ha movido la ventana")
                                window_moves+=1
                                if window_moves == len(data_list):
                                    self.set_seq(self.seq+window_size)
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
                                    self.set_number_of_sent_segments(self.number_of_sent_segments+1)
                                    self.socket.sendto(current_segment, self.otherAddress)
                                    print("Cliente: Se envió el trozo de SEQ = "+str(seqs[(i+(aSeq-seqY))%window_size]))
                                    timeout_list.start_timer((int(dictSegment["[SEQ]"])-seqY)%window_size)
                            else:
                                break

    def recv_using_selective_repeat(self):

        print("Server: Comienza Selective Repeat!")

        window_size = self.window_size
        seqY = self.seq
        if (self.messageIsComplete == True):
            firstSeq = seqY
            self.set_otherMessage("".encode())
            message_length = 0
            self.set_messageIsComplete(False)
        else:
            firstSeq = ((self.lastSeq+1-seqY)%(window_size*2))+seqY
            message_length = self.otherMessageLen - len(self.otherMessage)
        recv_window = sw.SlidingWindow(window_size, [], seqY)
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
                if message_length == 0 and int(dictMessage["[SEQ]"]) == seqY and dictMessage["[DATOS]"].isnumeric():
                    print("Server: Se recibió el largo del mensaje!")
                    message_length = int(dictMessage["[DATOS]"])
                    self.set_otherMessageLen(message_length)
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
                            bytesSoFar += len(recv_window.get_data(0).encode())
                            received[current_seq - seqY] = 0
                            if not (next_seq == seqY and messageSoFar == ""):
                                messageSoFar += recv_window.get_data(0)
                            recv_window.move_window(1)
                            firstSeq = ((firstSeq-seqY+1)%(window_size*2))+seqY
                            next_seq = ((current_seq-seqY+1)%(window_size*2))+seqY
                            print("Server: se ha movido la ventana")
                            seqs[(next_seq - seqY) % window_size] = (next_seq + window_size)%(window_size*2)
                            if bytesSoFar >= min(message_length, buff_size) and message_length > 0:
                                if message_length > buff_size and bytesSoFar >= buff_size:
                                    self.set_messageIsComplete(False)
                                self.set_otherMessage(self.otherMessage+messageSoFar.encode())
                                if len(self.otherMessage) >= message_length:
                                    self.set_messageIsComplete(True)
                                    self.set_seq(self.seq+window_size)
                                return messageSoFar.encode(), self.otherAddress
                        else:
                            break
                elif seqs.count(int(dictMessage["[SEQ]"])) == 0:
                    print("Server: se recibió un SEQ anterior ("+dictMessage["[SEQ]"]+")")
                    dictAck = {
                        "[SYN]": "0",
                        "[ACK]": "1",
                        "[FIN]": "0",
                        "[SEQ]": dictMessage["[SEQ]"],
                        "[DATOS]": ""
                    }
                    ack_segment = socketTCP.create_segment(dictAck)
                    self.socket.sendto(ack_segment, self.otherAddress)
                elif seqs.count(int(dictMessage["[SEQ]"])) > 0 and (message_length > 0 or not (dictMessage["[DATOS]"].isnumeric())):
                    
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
                    
                    if (received[int(dictMessage["[SEQ]"])-seqY] == 0):
                        print("Server: Se recibió un segmento de SEQ = " + dictMessage["[SEQ]"])
                        received[int(dictMessage["[SEQ]"])-seqY] = 1
                        next_seq = int(dictMessage["[SEQ]"])
                        if window_index == 0:
                            while True:
                                if received[next_seq - seqY] == 1:
                                    current_seq = recv_window.get_sequence_number(0)
                                    bytesSoFar += len(recv_window.get_data(0).encode())
                                    received[current_seq - seqY] = 0
                                    messageSoFar += recv_window.get_data(0)
                                    self.set_lastSeq(current_seq)
                                    recv_window.move_window(1)
                                    firstSeq = ((firstSeq-seqY+1)%(window_size*2))+seqY
                                    next_seq = ((current_seq-seqY+1)%(window_size*2))+seqY
                                    print("Server: se ha movido la ventana")
                                    seqs[(next_seq - seqY) % window_size] = (next_seq + window_size)%(window_size*2)
                                    if bytesSoFar >= min(message_length, buff_size) and message_length > 0:
                                        if message_length > buff_size and bytesSoFar >= buff_size:
                                            self.set_messageIsComplete(False)
                                        self.set_otherMessage(self.otherMessage+messageSoFar.encode())
                                        if len(self.otherMessage) >= message_length:
                                            self.set_messageIsComplete(True)
                                            self.set_seq(self.seq+window_size)
                                        return messageSoFar.encode(), self.otherAddress
                                else:
                                    break
                    else:
                        print("Server: se volvió a recibir un SEQ ("+dictMessage["[SEQ]"]+")")




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
    
    # ACTIVIDAD CONTROL DE CONGESTION

    def send_using_go_back_n(self, message: bytes):
        # dividimos el mensaje en trozos de 16 bytes
        message_length = (str(len(message))).encode()
        max_data_size_per_segment = 16
        # dejamos el primer elemento de data_list como el message_length (bytes de un string con el numero)
        data_list = [message_length] + self.create_message_slices(message, max_data_size_per_segment)

        # queremos partir después desde el ultimo numero de secuencia que recordamos, asi que anadimos datos "vacios"
        data_list = self.add_padding_to_data_list(data_list, self.seq)

        # creamos una ventana con el data_list + padding
        initial_seq = self.get_last_seq_from_handshake()
        sender_window = sw.SlidingWindow(self.window_size, data_list, initial_seq)

        # movemos la ventana para que la secuencia parta despues del padding o relleno
        sender_window = self.move_window_to_data_start(sender_window)

        # creamos un timer usando TimerList, en go back N tenemos 1 unico timer por ventana
        # asi que hacemos que nuestro timer_list sea de tamaño 1 y usamos el timeout del constructor de SocketTCP
        timer_list = tm.TimerList(self.timeout, 1)
        t_index = 0

        # enviamos la ventana inicial
        for wnd_index in range(self.window_size):
            # partimos armando y enviando el primer segmento
            current_data = sender_window.get_data(wnd_index)
            # si current_data == None, no quedan cosas en la ventana y salimos del for
            if current_data is None:
                break
            current_seq = sender_window.get_sequence_number(wnd_index)

            current_segment = self.create_data_segment(current_seq, current_data)
            self.send_con_perdidas(current_segment, self.destiny_address)

            if wnd_index == 0:
                # despues de enviar el primer elemento de la ventana corre el timer
                timer_list.start_timer(t_index)
            else:
                self.update_seq_number()

        # para poder usar este timer vamos poner nuestro socket como no bloqueante
        self.socket_udp.setblocking(False)

        # y para manejar esto vamos a necesitar un while True
        while True:
            try:
                # en cada iteración vemos si nuestro timer hizo timeout
                timeouts = timer_list.get_timed_out_timers()

                # si hizo timeout reenviamos toda la ventana
                if len(timeouts) > 0:
                    timer_list.stop_timer(t_index)
                    for i in range(self.window_size):
                        # partimos armando y enviando el primer segmento
                        wnd_index = i
                        current_data = sender_window.get_data(wnd_index)
                        if current_data is None:
                            timer_list.start_timer(t_index)
                            break
                        current_seq = sender_window.get_sequence_number(wnd_index)
                        self.seq = current_seq
                        current_segment = self.create_data_segment(current_seq, current_data)
                        self.send_con_perdidas(current_segment, self.destiny_address)
                        if wnd_index == 0:
                            # despues de enviar el primer elemento de la ventana corre el timer
                            timer_list.start_timer(t_index)

                # si no hubo timeout esperamos el ack del receptor
                answer, address = self.socket_udp.recvfrom(self.buff_size_udp)

            except BlockingIOError:
                # como nuestro socket no es bloqueante, si no llega nada entramos aquí y continuamos (hacemos esto en vez de usar threads)
                continue

            else:
                # si no entramos al except (y no hubo otro error) significa que llegó algo!
                # si lo que llegó es el syn_ack del accept (es decir se perdió el último ack del handshake) reenviamos ese ack y NO DETENEMOS EL TIMER
                # queremos que llegue al timeout y se reenvie la ventan
                if self.check_syn_ack(answer, self.expected_syn_ack_seq_number()):
                    # reenviamos el ultimo ack del handshake
                    self.send_con_perdidas(self.last_ack_from_handshake(), self.destiny_address)

                # si la respuesta es un ack válido
                if self.is_valid_ack_go_back_n(sender_window, answer):
                    # detenemos el timer
                    timer_list.stop_timer(t_index)
                    # calculamos cuanto se debe mover la ventana
                    steps_to_move = self.steps_to_move_go_back_n(sender_window, answer)
                    # movemos la ventana de a 1 paso mientras enviamos los segmentos correspondientes
                    wnd_index = self.window_size - 1

                    for k in range(1, steps_to_move + 1):
                        sender_window.move_window(1)
                        current_data = sender_window.get_data(wnd_index)
                        # si hay algo por mandar, lo mando
                        if current_data is not None:
                            current_seq = sender_window.get_sequence_number(wnd_index)
                            self.seq = current_seq
                            current_segment = self.create_data_segment(current_seq, current_data)
                            self.send_con_perdidas(current_segment, self.destiny_address)
                            # si es el primer elemento de la ventana, inicio el timer
                            if k == 1:
                                timer_list.start_timer(t_index)
                            # si no, me preocupo de mantener consistente el numero de secuencia que recuerda el socket
                            else:
                                self.update_seq_number()
                        else:
                            timer_list.start_timer(t_index)

                    # si luego de avanzar en la ventana, el primer elemento es None, significa que recibimos un ACK para cado elemento
                    if sender_window.get_data(0) is None:
                        # dejamos que el numero de secuencia apunte a donde debe comenzar la siguiente ventana
                        self.update_seq_number()
                        # y retornamos (ya recibimos todos los ACKs)
                        return

    def recv_using_go_back_n(self, buff_size: int) -> bytes:
        # si tenia un timeout activo en el objeto, lo desactivo
        self.socket_udp.settimeout(None)

        expected_seq = self.seq

        # inicializamos el mensaje total. La función start_current_message retorna b'' si espero un nuevo mensaje
        # y puede partir con algo diferente si me quedo una trozo de mensaje guardado desde una llamada de recv anterior
        full_message = self.get_message_reminder()

        # si el mensaje es nuevo (no estamos a la mitad de recibir un mensaje), esperamos el message_length
        if self.expecting_new_message():
            # esperamos el largo del mensaje
            while True:
                first_message_slice, address = self.socket_udp.recvfrom(self.buff_size_udp)
                # si es el numero de secuencia que esperaba, extraigo el largo del mensaje
                if self.check_seq(first_message_slice, expected_seq) and not self.check_ack(first_message_slice, expected_seq):
                    # la funcion get_message_length_from_segment retorna el message_length en int
                    message_length = self.get_message_length_from_segment(first_message_slice)

                    # le indicamos al socket cuantos bytes debera recibir
                    self.set_bytes_to_receive(message_length)

                    # respondemos con el ack correspondiente
                    current_ack = self.create_ack(expected_seq)
                    self.send_con_perdidas(current_ack, self.destiny_address)

                    # recordamos lo ultimo que mandamos
                    self.last_segment_sent = current_ack

                    # actualizamos el SEQ esperado
                    self.update_seq_number()

                    # salimos del loop
                    break
                # si el número de secuencia no es lo que esperaba, reenvio el ultimo segmento
                else:
                    # reenviamos lo ultimo que mandamos
                    self.send_con_perdidas(self.last_segment_sent, self.destiny_address)

        # reviso si recibi el mensaje completo, pero no lo pude retornar antes y tengo un trozo guardado
        if self.can_return_reminder_message():
            # cortamos el mensaje para que su tamaño maximo sea buff_size
            message_to_return = full_message[0:buff_size]
            message_reminder = full_message[buff_size:len(full_message)]

            # si sobra un trozo de mensaje lo guardamos
            self.save_message_reminder(message_reminder)
            return message_to_return

        # despues de recibir el message_length se continua con la recepcion
        while True:
            expected_seq = self.seq
            message_slice, address = self.socket_udp.recvfrom(self.buff_size_udp)

            # si es el numero de secuencia que esperaba, extraigo los datos
            if self.check_seq(message_slice, expected_seq):
                message_slice_data = self.get_data_from_segment(message_slice)
                full_message += message_slice_data
                # actualizamos la cantidad de bytes que nos queda por recibir
                self.update_bytes_to_receive(len(message_slice_data))

                # respondemos con el ack correspondiente
                current_ack = self.create_ack(expected_seq)
                self.send_con_perdidas(current_ack, self.destiny_address)

                # recordamos lo ultimo que mandamos
                self.last_segment_sent = current_ack

                # actualizamos el SEQ esperado
                self.update_seq_number()

                # verificamos si hay que retornar
                if len(full_message) >= buff_size or self.get_bytes_to_receive() == 0:
                    # cortamos el mensaje para que su tamaño maximo sea buff_size
                    message_to_return = full_message[0:buff_size]
                    message_reminder = full_message[buff_size:len(full_message)]

                    # si sobra un trozo de mensaje lo guardamos
                    self.save_message_reminder(message_reminder)
                    return message_to_return
            else:
                # reenviamos lo ultimo que mandamos
                self.send_con_perdidas(self.last_segment_sent, self.destiny_address)
    
    def set_loss_probability(self, loss_probability: int):
        """Cambia el parametro loss_probability dentro del objeto. Este parametro se utiliza para probar perdidas de forma manual (sin usar netem)."""
        self.loss_probability = loss_probability

    def set_debug_on(self):
        self.DEBUG = True

    def set_debug_off(self):
        self.DEBUG = False

    def send_con_perdidas(self, segment: bytes, address: (str, int)):
        """Funcion que fuerza perdidas al llamar a send. Si no desea utilizarla puede poner su tasa de perdida en 0 llamando a set_loss_probability"""
        # sacamos un número entre 0 y 100 de forma aleatoria
        random_number = random.randint(0, 100)

        # si el random_number es mayor o igual a la probabilidad de perdida enviamos el mensaje
        if random_number >= self.loss_probability:
            self.socket_udp.sendto(segment, address)
            if self.DEBUG:
                print(f"Se envió: {segment}")
        else:
            if self.DEBUG:
                print(f"Oh no, se perdió: {segment}")

    def add_padding_to_data_list(self, data_list: list, SEQ: int) -> list:
        """Rellena la lista de datos con b'' para que el numero de secuencia inicial calce con SEQ."""
        i = 0
        n = self.window_size
        padding = []
        while i % (2 * n) + self.initial_seq != SEQ:
            padding.append(b'')
            i += 1
        return padding + data_list

    @staticmethod
    def move_window_to_data_start(sliding_window: sw.SlidingWindow) -> sw.SlidingWindow:
        """Mueve una ventana hasta que comienzan los datos (es decir, se mueve hasta no ver el relleno de b'' o padding)"""
        while sliding_window.get_data(0) == b'':
            sliding_window.move_window(1)
        return sliding_window

    def save_expected_syn_ack_seq_number(self, SEQ: int):
        self.expected_seq = SEQ

    def expected_syn_ack_seq_number(self):
        return self.expected_seq

    def save_last_ack_from_handshake(self):
        """Durante el handshake se debe guardar el ultimo ACK enviado, de esta forma si al llamar a send se recibe dicho SYN ACK podremos reenviar dicho ACK. Esta funcion debe ser implementada
        por ud."""
        pass

    def last_ack_from_handshake(self):
        return self.last_ack

    def save_message_reminder(self, message: bytes):
        """Si al llamar recv es necesario retornar una cantidad de bytes menor que la que se ha recibido, entonces se guarda el sobrante para retornarlo en una siguiente llamada de recv.
        Esta funcion debe ser implementada por ud."""
        pass

    def can_return_reminder_message(self) -> bool:
        """Verifica si es posible retornar solo utilizando el resto de mensaje guardado dentro del objeto SocketTCP, es decir, retorna True si ya se recibieron todos los bytes del mensaje desde el
        sender, pero quedaba un resto de bytes que no habia sido retornado previamente. Este resto fue previamente guardado usando la funcion save_message_reminder. Esta funcion debe ser
        implementada por ud."""
        pass

    def expecting_new_message(self) -> bool:
        """Determina si se esta esperando un nuevo mensaje en recv (es decir esperamos que el primer mensaje traiga el message_length). Esta funcion debe ser implementada por ud."""
        pass

    def get_last_seq_from_handshake(self) -> int:
        """Retorna el ultimo numero de secuencia del handshake. Este numero es el mismo para el socket que llama a connect y el socket que llama a accept. Esta funcion debe ser implementada por ud."""
        pass

    def get_message_reminder(self) -> bytes:
        """Retorna el resto de mensaje guardado por la funcion save_message_reminder. Si no hay un resto guardado debe retornar b''. Esta funcion debe ser implementada por ud."""
        pass

    def get_data_from_segment(self, segment: bytes) -> bytes:
        """Extrae los datos desde un segmento en bytes. Esta funcion debe ser implementada por ud."""
        pass

    def get_message_length_from_segment(self, segment: bytes) -> int:
        """Extrae el message_length desde el segmento en bytes. El message_length se retorna como int. Esta funcion debe ser implementada por ud."""
        pass

    def get_bytes_to_receive(self) -> int:
        """Indica cuantos bytes quedan por recibir, este parametro debe almacenarse dentro del objeto SocketTCP. Esta funcion debe ser implementada por ud."""
        pass

    def set_bytes_to_receive(self, message_length: int):
        """Guarda el message_length para saber cuantos bytes se deberan recibir. Esta funcion debe ser implementada por ud."""
        pass

    def update_bytes_to_receive(self, message_slice: int):
        """Actualiza la cantidad de datos que queda por recibir dado que llego message_slice. Esta funcion debe ser implementada por ud."""
        pass

    def create_message_slices(self, message: bytes, max_data_size_per_segment: int) -> list:
        """Dado un mensaje bytes message, crea una lista con trozos del mensaje de tamaño maximo max_data_size_per_segment. Cada elemento en la lista retornada es de tipo bytes. Esta funcion debe ser
        implementada por ud."""
        pass

    def create_syn(self, SEQ: int) -> bytes:
        """Crea un segmento SYN con numero de secuencia SEQ, usa la funcion create_segment y retorna bytes. Esta funcion debe ser implementada por ud."""
        pass

    def create_syn_ack(self, SEQ: int) -> bytes:
        """Crea un segmento SYN-ACK con numero de secuencia SEQ, usa la funcion create_segment y retorna bytes. Esta funcion debe ser implementada por ud."""
        pass

    def create_ack(self, SEQ: int) -> bytes:
        """Crea un segmento ACK con numero de secuencia SEQ, usa la funcion create_segment y retorna bytes. Esta funcion debe ser implementada por ud."""
        pass

    def create_data_segment(self, SEQ: int, DATA: bytes) -> bytes:
        """Crea un segmento de datos con numero de secuencia SEQ y contenido DATA. Usa la funcion create_segment y retorna bytes. Esta funcion debe ser implementada por ud."""
        pass

    def check_syn_ack(self, segment: bytes, SEQ: int) -> bool:
        """Checkea si el segmento segment es un SYN-ACK con numero de secuencia SEQ. Esta funcion debe ser implementada por ud."""
        pass

    def check_ack(self, segment: bytes, expected_seq: int) -> bool:
        """Checkea si el segmento segment es un ACK con numero de secuencia expected_seq. Esta funcion debe ser implementada por ud."""
        pass

    def check_seq(self, segment: bytes, expected_seq: int) -> bool:
        """Checkea si el segmento segment tiene numero de secuencia expected_seq. Esta funcion debe ser implementada por ud."""
        pass

    def is_valid_ack_go_back_n(self, sliding_window: sw.SlidingWindow, answer: bytes) -> bool:
        """Checkea si el segmento answer tiene numero de secuencia correcto para Go Back N"""
        parsed_answer = self.parse_segment(answer)
        answer_seq = parsed_answer["SEQ"]
        is_ack = parsed_answer["SEQ"]
        for i in range(sliding_window.window_size):
            if is_ack and sliding_window.get_sequence_number(i) == answer_seq:
                return True
        return False

    def update_seq_number(self):
        """Actualiza el numero de secuencia. Cada vez que se llama el numero de secuencia aumenta en 1 (asume que los numeros de secuencia se rigen por ventanas deslizantes tipo SlidingWindow). """
        self.segment_count += 1
        i = self.segment_count
        n = self.window_size
        self.seq = self.initial_seq + i % (2 * n)

    def bind_to_new_address(self, original_socketTCP_address: (str, int)):
        """Asocia un socket tipo SocketTCP a una diección distinta de original_socketTCP_address. Esta funcion debe ser implementada por ud."""
        pass

    def steps_to_move_go_back_n(self, sender_window: sw.SlidingWindow, received_segment: bytes) -> int:
        """Determina la cantidad de pasos que la ventana deslizante sender_window se debe mover dado que se recibio el segmento receibed_segment."""
        wnd_size = sender_window.window_size
        parsed_segment = self.parse_segment(received_segment)
        seq_num = parsed_segment["SEQ"]
        for i in range(wnd_size):
            if seq_num == sender_window.get_sequence_number(i):
                return i + 1
        else:
            return -1