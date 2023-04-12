import socket
import requests
import json
import httplib2


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

    """ head_decode = full_head.decode()
    after_head = head_decode.split(end_head, 1)[1]
    print(head_decode)
    content_length = (head_decode.split("Content-Length: ", 1)[1]).split("\r\n", 1)[0]
    body_list = receive_body(connection_socket, buff_size, int(content_length), after_head)
    head_list.append((recv_http.decode()).split(end_head, 1)[0] + end_head) """

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
    after_head = head_decode.split(end_head, 1)[1]
    print(head_decode)
    content_length = (head_decode.split("Content-Length: ", 1)[1]).split("\r\n", 1)[0]
    body_list = receive_body(connection_socket, buff_size, int(content_length), after_head)
    head_list.append((recv_http.decode()).split(end_head, 1)[0] + end_head)

    return head_list, body_list


def receive_body(connection_socket, buff_size, content_length, body_start):
    body_list = list()
    body_list.append(body_start)
    num_bytes = len(body_start.encode('utf-8'))

    while num_bytes < content_length:
        recv_body = connection_socket.recv(buff_size)
        num_bytes += 4
        body_list.append(recv_body.decode())

    return body_list


def send_http(head_list):
    if ("GET" in head_list[0]):
        http_string = ''.join(head_list)
        # print(http_string)
        adressRequest = (http_string.split("GET", 1)[1].split("HTTP", 1))[0].replace(" ", "")
        # host = (http_string.split("Host: ", 1)[1].split("\r\n", 1))[0].replace(" ", "")
        # response = requests.get("http://example.com")
        client_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ip = socket.gethostbyname("example.com")
        print(str(id) + " hola")
        address = ("example.com", 80)
        client_proxy.connect(address)
        client_proxy.send(http_string.encode())
        buffer_size = 1024
        HEAD, BODY = receive_head(client_proxy, buffer_size, "\r\n\r\n")
        head_string = ''.join(HEAD)
        body_string = ''.join(BODY)
        """ dict = list(response.headers.keys())
        HEAD = ""
        HEAD += (http_string.split(" ", 2)[2].split("\r\n", 1))[0].replace(" ", "")
        HEAD += " " + str(response.status_code) + " " + response.reason + "\r\n"
        for keys in dict:
            HEAD += keys + ": " + response.headers[keys] + "\r\n" """
        with open("/home/franz/Escritorio/RedesGit/Redes/Redes/Ejemplo_cliente_y_servidor_orientados_a_conexion/name_user.json") as file:
            data = json.load(file)
            name_user = data['users'][0]["nombre"]
        head_string = head_string[:-4]
        head_string += "X-ElQuePregunta: "+name_user+"\r\n\r\n"   
        HTTP = head_string + body_string
        return HTTP



buff_size = 4
end_of_head = "\r\n\r\n"
new_socket_address = ('localhost', 8000)

print('Creando socket - Proxy')

proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

proxy_socket.bind(new_socket_address)

proxy_socket.listen(3)

print('... Esperando clientes')
while True:
    new_socket, new_socket_address = proxy_socket.accept()
    recv_head = receive_http(new_socket, buff_size, end_of_head)

    print('Se ha recibido el HTTP')

    response = send_http(recv_head)
    new_socket.send(response.encode())

    print('Se ha recibido la response')

    new_socket.close()
    print(f"conexión con {new_socket_address} ha sido cerrada")
