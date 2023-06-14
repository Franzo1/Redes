import sys
import socket

# python3 prueba_router.py headers IP_router_inicial puerto_router_inicial

headers = sys.argv[1]
IP_router_inicial = sys.argv[2]
puerto_router_inicial = sys.argv[3]

txt_file = open("holi.txt", "r")
file_list = txt_file.readlines()

test_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

for line in file_list:
    test_socket.sendto((headers+","+line).encode(), (IP_router_inicial, int(puerto_router_inicial))) 