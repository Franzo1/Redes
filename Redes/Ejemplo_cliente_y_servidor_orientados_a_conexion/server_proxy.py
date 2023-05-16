import socket
import json

def receive_http(connection_socket, buff_size, end_head):
    
    head_list = list()
    recv_http = connection_socket.recv(buff_size)
    full_head = recv_http

    is_end_of_head = end_head in full_head.decode()

    while not is_end_of_head:
        
        head_list.append(recv_http.decode())
        recv_http = connection_socket.recv(buff_size)
        full_head += recv_http
        is_end_of_head = end_head in full_head.decode()

    head_list.append(recv_http.decode())

    return head_list

def receive_head(connection_socket, buff_size, end_head):
    
    head_list = list()
    recv_http = connection_socket.recv(buff_size)
    full_head = recv_http

    is_end_of_head = end_head in full_head.decode()

    while not is_end_of_head:
        
        head_list.append(recv_http.decode())
        recv_http = connection_socket.recv(buff_size)
        full_head += recv_http
        is_end_of_head = end_head in full_head.decode()

    head_decode = full_head.decode()
    bytes_head = len(full_head)
    content_length = int((head_decode.split("Content-Length: ", 1)[1]).split("\r\n", 1)[0])
    after_head = head_decode.split(end_head, 1)[1]
    bytes_afhead = len(after_head.encode('utf-8'))
    head_decode = head_decode.split(end_head, 1)[0] + end_head
    print(head_decode)

    if bytes_head + content_length > buff_size:
        if content_length - bytes_afhead > buff_size:
            body_string = receive_huge_body(connection_socket, buff_size, int(content_length), after_head)
        else:
            body_string = receive_body(connection_socket, after_head)
        head_list.append(recv_http.decode().split("\r\n\r\n")[0]+"\r\n\r\n")
    else:
        body_string = ""
        head_list.append(full_head.decode())

    print("".join(head_list))
    return head_list, body_string

def receive_body(connection_socket, body_start):
    
    recv_body = connection_socket.recv(buff_size)
    body_start += recv_body.decode()
    
    return body_start


def receive_huge_body(connection_socket, buff_size, content_length, body_start):
    
    body_list = list()
    bytes_body = body_start.encode()
    num_bytes = len(body_start.encode('utf-8'))

    while num_bytes < content_length:
        recv_body = connection_socket.recv(buff_size)
        body_list.append(recv_body)
        num_bytes += buff_size

    for i in body_list:
        bytes_body += i

    string_body = bytes_body.decode()

    return string_body


def send_http(head_list, buffer_size):
    
    if ("GET" in head_list[0]):
        
        http_string = ''.join(head_list)
        adressRequest = (http_string.split("GET ", 1)[1].split(" HTTP", 1))[0].replace(" ", "")
        
        with open("/home/franz/Escritorio/RedesGit/Redes/Redes/Ejemplo_cliente_y_servidor_orientados_a_conexion/json_actividad_http.json") as file:
            data = json.load(file)
            blocked_list = data['blocked']
        
        if adressRequest in blocked_list:
            return 'HTTP/1.1 403 Forbidden\r\n\r\n<html><head><title>403 Forbidden</title></head><body bgcolor="white"><center><h1>403 Forbidden</h1></center></body></html>'
        else:
            
            adressHost = (http_string.split("Host: ", 1)[1].split("\r\n", 1))[0].replace(" ", "")
            client_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            address = (adressHost, 80)
            client_proxy.connect(address)
            
            with open("/home/franz/Escritorio/RedesGit/Redes/Redes/Ejemplo_cliente_y_servidor_orientados_a_conexion/name_user.json") as file:
                dataName = json.load(file)
                name_user = dataName['users'][0]["nombre"]

            client_proxy.send(http_string.encode())
            
            HEAD, BODY = receive_head(client_proxy, buffer_size, "\r\n\r\n")
            head_string = ''.join(HEAD)
            forbidden_list = data["forbidden_words"]
            
            head_string1 = head_string.split("\r\n\r\n", 1)[0]
            head_string2 = head_string.split("\r\n\r\n", 1)[1]
            head_string1 += "\r\nX-ElQuePregunta: "+name_user+"\r\n\r\n" 
            head_string = head_string1 + head_string2
            HTTP = head_string + BODY

            for i in forbidden_list:
                word = list(i.keys())[0]
                if word in HTTP:
                    HTTP = HTTP.replace(word,i[word])

            return HTTP



buff_size = 40
end_of_head = "\r\n\r\n"
new_socket_address = ('localhost', 8001)

print('Creando socket - Proxy\n')

proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

proxy_socket.bind(new_socket_address)

proxy_socket.listen(1)

print('... Esperando clientes\n')
while True:
    new_socket, new_socket_address = proxy_socket.accept()
    recv_http= receive_http(new_socket, buff_size, end_of_head)

    print('Se ha recibido el HTTP request\n')

    response = send_http(recv_http, buff_size)
    print('Respuesta del servidor:\n')
    print(response)
    print(bytes(response, 'utf-8'))
    new_socket.send(response.encode())

    print('Se ha reenviado la response\n')

    new_socket.close()
    print(f"conexión con {new_socket_address} ha sido cerrada\n")
