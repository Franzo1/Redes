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
router_routes = sys.argv[3]

print("Se ha creado un router en la dirección (" + str(router_IP) + ", " + str(router_port) + ")")

router_address = (str(router_IP), int(router_port))

router_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
router_socket.bind(router_address)
router_socket.setblocking(True)

while True:
    
    received_message, server_address = router_socket.recvfrom(24)
    parsed_message = parse_packet(received_message)
    destination_address = (str(parsed_message["IP"]), int(parsed_message["PORT"]))
    
    if router_address == destination_address:
        print("Se recibió el siguiente mensaje: " + str(parsed_message["MESSAGE"]))
    else:
        next_hop = check_routes(router_routes, destination_address)
        if next_hop == None:
            print("No hay rutas hacia " + str(destination_address) + ' para paquete "' + str(parsed_message["MESSAGE"]) + '"')
        else:
            print('Redirigiendo paquete "' + str(parsed_message["MESSAGE"]) + '" con destino final ' + str(destination_address) + " desde " + str(router_address) + " hacia " + str(next_hop))
            router_socket.sendto(received_message, next_hop) 
