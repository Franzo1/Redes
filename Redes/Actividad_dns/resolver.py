import socket
from dnslib import DNSRecord, DNSHeader, DNSQuestion
from dnslib.dns import CLASS, QTYPE, RR, A
import dnslib

Root_IP = "192.33.4.12"
buff_size = 4096


def resolver(mensaje_consulta):
    
    dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    address = (Root_IP, 53)
    dns_socket.sendto(mensaje_consulta, address)

    answer, _ = dns_socket.recvfrom(buff_size)
    parsed_answer, info = query_parser(answer)
    count = 0

    hasTypeA = False

    print(info[1])

    if info[1] > 0:
        rrs = list()
        while count < info[1]:
            rrs.append(parsed_answer.get_a())
            count += 1
        
        for i in rrs:
            print(i.rtype)
            if i.rtype == A:
                hasTypeA = True

    if hasTypeA:
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

address = ('localhost', 8000)

resolver_socket.bind(address)

while True:

    query_rcv, address = resolver_socket.recvfrom(buff_size)

    print("\r\n")
    print(query_rcv)
    print("\r\n")
    query_parse, info = query_parser(query_rcv)
    print(query_parse)
    print("\r\n")
    answer = resolver(query_rcv)

resolver_socket.close()