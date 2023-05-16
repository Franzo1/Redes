import socket
from dnslib import DNSRecord
from dnslib.dns import QTYPE, A, NS
import dnslib

Root_IP = "192.33.4.12"
buff_size = 4096

def sendAndRecv(mensaje_consulta, address, dns_socket):

    dns_socket.sendto(mensaje_consulta, address)

    answer, _ = dns_socket.recvfrom(buff_size)
    parsed_answer, info = query_parser(answer)

    print(parsed_answer)

    hasTypeA = False

    if info[1] > 0:
        
        for i in info[4]:
            if i.rtype == A:
                hasTypeA = True


    if hasTypeA:
        return answer
    
    else:
        
        hasTypeNS = False
        
        for i in info[5]:
            type = QTYPE.get(i.rtype)
            type = i.rdata 
            if type == NS:
                hasTypeNS = True
        
        if hasTypeNS:

            hasAinNS = False
        
            for i in info[6]:
                artype = QTYPE.get(i.rclass) 
                if artype == A:
                    hasAinNS = True
            
            if hasAinNS:
                
                foundIP = False
                
                for i in info[6]:
                    if i.rdata != None and not foundIP:
                        firstIP = i.rdata
                        foundIP = True
                
                if foundIP:
                    address = (str(firstIP), 53)
                    dns_socket.sendto(mensaje_consulta, address)
                    answer, _ = dns_socket.recvfrom(buff_size)
                    return answer
                
                else:
                    rd = info[5][0].rdata
                    if isinstance(rd, dnslib.dns.SOA):
                        name_server = rd.get_mname() 
                    elif isinstance(rd, dnslib.dns.NS):
                        name_server = rd
                    address = (str(name_server), 53)
                    q = DNSRecord.question(name_server).pack()
                    answer = resolver(q)
                    answer_parsed, info = query_parser(answer)
                    first_answer = answer_parsed.get_a()
                    ip = str(first_answer.rdata)
                    address = (ip, 53)
                    dns_socket.sendto(mensaje_consulta, address)
                    answer, _ = dns_socket.recvfrom(buff_size)
                    return answer

        
        else:
            print("Ignored")

    


def resolver(mensaje_consulta):

    success = False
    dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (Root_IP, 53)
    while not success:
        answer = sendAndRecv(mensaje_consulta, address, dns_socket)
        _, info = query_parser(answer)
        if info[1] > 0:
            success = True
    return answer
    




def query_parser(query):
    
    query_parse = DNSRecord.parse(query_rcv)
    info = list()
    # Appends: Qname, ANCOUNT, NSCOUNT, ARCOUNT, Answer, Authority, Additional
    info.append((query_parse.get_q()).get_qname())
    info.append(query_parse.header.a)
    info.append(query_parse.header.auth)
    info.append(query_parse.header.ar)
    info.append(query_parse.rr)
    info.append(query_parse.auth)
    info.append(query_parse.ar)

    return query_parse, info

resolver_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

local_address = ('localhost', 8000)

resolver_socket.bind(local_address)

while True:

    query_rcv, address = resolver_socket.recvfrom(buff_size)
    query_parse, info = query_parser(query_rcv)
    print("Se resuelve la query:\r\n")
    print(query_parse)
    answer = resolver(query_rcv)
    resolver_socket.sendto(answer, address)

    resolver_socket.close()