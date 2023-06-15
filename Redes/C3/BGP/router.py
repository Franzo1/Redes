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
        str_packet += str(i) + ","
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
    copy = parsed_packet.copy()
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
            copy["MESSAGE"] = (message.encode())[first_byte:last_byte].decode()
            first_byte = last_byte
            if last_byte >= len(message.encode()):
                finished = True
                if og["FLAG"] == "0":
                    copy["FLAG"] = "0"
            fragment_list += [create_packet(copy).encode()]
            if finished:
                break
        return fragment_list

def reassemble_IP_packet(fragment_list):
    if len(fragment_list) == 1:
        parsed_fragment = parse_packet(fragment_list[0])
        if parsed_fragment["OFFSET"] == "0" and parsed_fragment["FLAG"] == "0":
            return parsed_fragment
        else:
            return None
    else:
        offset = -1
        for fragment in fragment_list:
            if int(parse_packet(fragment)["OFFSET"]) == 0:
                offset = 0
        if offset == -1:
            return None
        i = 0
        x = 0
        message = ""
        while True:
            parsed_fragment = parse_packet(fragment_list[i])
            if int(parsed_fragment["OFFSET"]) == offset:
                message += str(parsed_fragment["MESSAGE"])
                offset += len(parsed_fragment["MESSAGE"].encode())
                x = 0
                if parsed_fragment["FLAG"] == "0":
                    reassembled_packet = parsed_fragment.copy()
                    reassembled_packet["OFFSET"] = "0"
                    reassembled_packet["SIZE"] = eigth_digits(len(message.encode()))
                    reassembled_packet["FLAG"] = "0"
                    reassembled_packet["MESSAGE"] = message
                    return reassembled_packet
            i = (i+1)%len(fragment_list)
            x += 1
            if x == len(fragment_list):
                return None

def create_BGP_message(router_routes, router_port):
    txt_file = open(router_routes, "r")
    router_table = txt_file.readlines()
    BGP_message = "BGP_ROUTES\n" + str(router_port) + "\n"
    for line in router_table:
        line_list = line.split(" ")
        i = 1
        while True:
            if line_list[i] == str(router_port):
                BGP_message += line_list[i] + "\n"
                break
            else:
                BGP_message += line_list[i] + " "
                i+=1
    BGP_message += "END_ROUTES"
    return BGP_message.encode()

def send_BPG_message(router_socket, router_routes, router_port, router_table):
    for line in router_table:
        line_list = line.split(" ")
        BGP_message = create_BGP_message(router_routes, router_port)
        router_socket.sendto(BGP_message, (line_list[0], int(line_list[1])))
    return BGP_message.decode()

def check_if_destination_exists(BGP_list, steps, router_table, line):
    for route in BGP_list:
        my_steps = route.split(" ")
        if steps[0] == my_steps[0]:
            if len(steps) < len(my_steps):
                new_routes = ""
                for my_route in router_table:
                    my_route_steps = my_route.split(" ")
                    if steps[0] == my_route_steps[1]:
                        new_routes += my_route_steps[0] + " " + line + " " + my_route_steps[0] + " " +steps[-2] + " " + my_route_steps[-1] + "\n"
                    else:
                        new_routes += my_route + "\n"
                    new_routes = new_routes[:-1]
                    txt_file = open(router_routes, "w")
                    txt_file.write(new_routes)
                    txt_file.close()
                return 1
    return 0

def run_BGP(router_socket, router_routes, router_port, router_IP):
    txt_file = open(router_routes, "r")
    router_table = txt_file.readlines()
    for line in router_table:
        line_list = line.split(" ")
        router_socket.sendto("START_BGP".encode(), (line_list[0], int(line_list[1])))
    BGP_message = send_BPG_message(router_socket, router_routes, router_port, router_table)
    BGP_list = BGP_message.split("\n")[2:-1]
    router_socket.settimeout(10)
    try:
        received_message, server_address = router_socket.recvfrom(1000)
        decoded_message = received_message.decode()
        if "BGP_ROUTES" in decoded_message:
            message_list = decoded_message.split("\n")[2:-1]
            for line in message_list:
                if not (router_port in line):
                    steps = line.split(" ")
                    if check_if_destination_exists(BGP_list, steps, router_table, line) == 0:
                        txt_file = open(router_routes, "a")
                        new_line = "\n" + router_IP + " " + line + " " + router_IP + " "
                        for my_route in router_table:
                            my_route_data = my_route.split(" ")
                            if my_route_data[-2] == steps[-2]:
                                new_line += str(my_route_data[-1])
                                break
                        txt_file.write(new_line)      
                        txt_file.close()

    except socket.timeout:
        print("Terminó BGP")
        return
    



router_IP = sys.argv[1]
router_port = sys.argv[2]
router_routes = sys.argv[3]

router_address = (str(router_IP), int(router_port))

router_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print("Se ha creado un router en la dirección (" + str(router_IP) + ", " + str(router_port) + ")")
router_socket.bind(router_address)
router_socket.setblocking(True)

fragments_dictionary = {}

while True:
    
    received_message, server_address = router_socket.recvfrom(1000)
    if "\n" in received_message.decode():
        received_message = (received_message.decode()[:-1]).encode()
    parsed_message = parse_packet(received_message)
    
    if int(parsed_message["TTL"]) <= 0:
        print("Se recibió paquete '" + str(parsed_message["ID"]) + "' con TTL 0")
    
    else:
        destination_address = (str(parsed_message["IP"]), int(parsed_message["PORT"]))
        
        if router_address == destination_address:
            print("Se recibió el siguiente mensaje: " + str(parsed_message["MESSAGE"]))
            if str(parsed_message["ID"]) in fragments_dictionary:
                fragments_dictionary[str(parsed_message["ID"])] = fragments_dictionary[str(parsed_message["ID"])] + [received_message]
            else:
                fragments_dictionary[str(parsed_message["ID"])] = [received_message]
            reassembled_packet = reassemble_IP_packet(fragments_dictionary[str(parsed_message["ID"])])
            if reassembled_packet != None:
                print("Mensaje final re-ensamblado: " + reassembled_packet["MESSAGE"])
        else:
            next_hop, mtu = check_routes(router_routes, destination_address)
            if next_hop == None:
                print("No hay rutas hacia " + str(destination_address) + ' para paquete "' + str(parsed_message["ID"]) + '"')
            else:
                print('Redirigiendo paquete "' + str(parsed_message["ID"]) + '" con destino final ' + str(destination_address) + " desde " + str(router_address) + " hacia " + str(next_hop))
                parsed_message["TTL"] = str(int(parsed_message["TTL"])-1)
                message_to_resend = create_packet(parsed_message)
                fragment_list = fragment_IP_packet(message_to_resend.encode(), mtu)
                for fragment in fragment_list:
                    router_socket.sendto(fragment, next_hop) 