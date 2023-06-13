import sys
import socket

def parse_packet(IP_packet):
    decoded_packet = IP_packet.decode()
    list_packet = decoded_packet.split(",")
    list_keys = ["IP","PORT","TTL","ID","OFFSET","SIZE","FLAG","MESSAGE"]
    dict_packet = dict(zip(list_keys,list_packet))
    return dict_packet

def create_packet(parsed_IP_packet):
    packet_values = parsed_IP_packet.values()
    str_packet = ""
    for i in packet_values:
        str_packet += i + ","
    str_packet = str_packet[:-1]
    return str_packet

line_index = 0

def check_routes(routes_file_name, destination_address):
    txt_file = open(routes_file_name, "r")
    router_table = txt_file.readlines()
    len_table = len(router_table)
    global line_index
    for i in range(0, len_table):
        line_index = line_index%len_table
        line_list = router_table[line_index].split(" ")
        line_index += 1
        if int(line_list[1]) <= destination_address[1] <= int(line_list[2]):
            return (line_list[3], int(line_list[4])), int(line_list[5])
    return None

def make_copy(parsed_packet, offset):
    copy = parsed_packet
    copy["OFFSET"] = offset
    copy["SIZE"] = "00000000"
    copy["FLAG"] = "1"
    copy["MESSAGE"] = ""
    return copy

def eigth_digits(num):
    str_num = str(num)
    while len(str_num) < 8:
        str_num = "0" + str_num
    return str_num

def fragment_IP_packet(IP_packet, MTU):
    full_size = len(IP_packet)
    if full_size <= MTU:
        return [IP_packet]
    else:
        og = parse_packet(IP_packet)
        fragment_list = []
        offset = og["OFFSET"]
        message = og["MESSAGE"]
        first_byte = 0
        last_byte = 0
        finished = False
        while True:
            copy = make_copy(og, offset)
            copy_header = create_packet(copy).encode()
            copy_header_len = len(copy_header)
            size = MTU - copy_header_len
            last_byte = first_byte + size
            offset = str(int(offset)+size)
            copy["SIZE"] = eigth_digits(size)
            copy["MESSAGE"] = (message.encode())[first_byte:last_byte]
            first_byte = last_byte
            if last_byte >= len(message.encode()):
                finished = True
                if og["FLAG"] == "0":
                    copy["FLAG"] = "0"
            fragment_list += [copy]
            if finished:
                break
        return fragment_list


router_IP = sys.argv[1]
router_port = sys.argv[2]
router_routes = sys.argv[3]

router_address = (str(router_IP), int(router_port))

router_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Se ha creado un router en la dirección (" + str(router_IP) + ", " + str(router_port) + ")")
router_socket.bind(router_address)
router_socket.setblocking(True)

while True:
    
    received_message, server_address = router_socket.recvfrom(100)
    if "\n" in received_message.decode():
        received_message = (received_message.decode()[:-1]).encode()
    parsed_message = parse_packet(received_message)
    print(fragment_IP_packet(received_message, 38))
    
    if int(parsed_message["TTL"]) <= 0:
        print("Se recibió paquete '" + str(parsed_message["MESSAGE"]) + "' con TTL 0")
    
    else:
        destination_address = (str(parsed_message["IP"]), int(parsed_message["PORT"]))
        
        if router_address == destination_address:
            print("Se recibió el siguiente mensaje: " + str(parsed_message["MESSAGE"]))
        else:
            next_hop, mtu = check_routes(router_routes, destination_address)
            if next_hop == None:
                print("No hay rutas hacia " + str(destination_address) + ' para paquete "' + str(parsed_message["MESSAGE"]) + '"')
            else:
                print('Redirigiendo paquete "' + str(parsed_message["MESSAGE"]) + '" con destino final ' + str(destination_address) + " desde " + str(router_address) + " hacia " + str(next_hop))
                parsed_message["TTL"] = str(int(parsed_message["TTL"])-1)
                message_to_resend = create_packet(parsed_message)
                router_socket.sendto(message_to_resend.encode(), next_hop) 
