import sys
import socket

def parse_packet(IP_packet):
    decoded_packet = IP_packet.decode()
    list_packet = decoded_packet.split(",")
    list_keys = ["IP","PORT","MESSAGE"]
    dict_packet = dict(zip(list_keys,list_packet))
    return dict_packet

def create_packet(parsed_IP_packet):
    packet_values = parsed_IP_packet.values()
    str_packet = ""
    for i in packet_values:
        str_packet += i + ","
    str_packet = str_packet[:-1]
    return str_packet

def check_routes(routes_file_name, destination_address):
    txt_file = open(routes_file_name, "r")
    router_table = txt_file.readlines()
    for line in router_table:
        line_list = line.split(" ")
        if int(line_list[1]) <= destination_address[1] <= int(line_list[2]):
            return (line_list[3], int(line_list[4])) 
    return None

router_IP = sys.argv[1]
router_port = sys.argv[2]

print("Se ha creado un router en la dirección (" + str(router_IP) + ", " + str(router_port) + ")")

router_address = (router_IP, router_port)

""" router_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
router_socket.bind(router_address)
router_socket.setblocking(True)

received_message, server_address = router_socket.recvfrom(24) """

print(check_routes(sys.argv[3], ("127.0.0.1", 8882)))