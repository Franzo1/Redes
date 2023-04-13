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
    content_length = int((head_decode.split("Content-Length: ", 1)[1]).split("\r\n", 1)[0])
    after_head = head_decode.split(end_head, 1)[1]
    head_decode = head_decode.split(end_head, 1)[0] + end_head
    body_list = receive_body(connection_socket, buff_size, int(content_length), after_head)
    head_list.append(head_decode)

    return head_list, body_list


def receive_body(connection_socket, buff_size, content_length, body_start):
    body_list = list()
    body_list.append(body_start)
    num_bytes = len(body_start.encode('utf-8'))

    while num_bytes < content_length:
        recv_body = connection_socket.recv(buff_size)
        body_list.append(recv_body.decode())
        num_bytes += buff_size

    return body_list


def send_http(head_list):
    if ("GET" in head_list[0]):
        http_string = ''.join(head_list)
        adressRequest = (http_string.split("GET ", 1)[1].split(" HTTP", 1))[0].replace(" ", "")
        with open("/home/franz/Escritorio/RedesGit/Redes/Redes/Ejemplo_cliente_y_servidor_orientados_a_conexion/json_actividad_http.json") as file:
            data = json.load(file)
            blocked_list = data['blocked']
        if adressRequest in blocked_list:
            return "HTTP/1.1 403 Forbidden\r\n\r\n"
        else:
            adressHost = (http_string.split("Host: ", 1)[1].split("\r\n", 1))[0].replace(" ", "")
            # host = (http_string.split("Host: ", 1)[1].split("\r\n", 1))[0].replace(" ", "")
            # response = requests.get("http://example.com")
            client_proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # ip = socket.gethostbyname("example.com")
            address = (adressHost, 80)
            client_proxy.connect(address)
            with open("/home/franz/Escritorio/RedesGit/Redes/Redes/Ejemplo_cliente_y_servidor_orientados_a_conexion/name_user.json") as file:
                dataName = json.load(file)
                name_user = dataName['users'][0]["nombre"]
            http_string = http_string[:-2]
            http_string += "X-ElQuePregunta: "+name_user+"\r\n\r\n"
            print(http_string)
            client_proxy.send(http_string.encode())
            HEAD, BODY = receive_head(client_proxy, 1024, "\r\n\r\n")
            head_string = ''.join(HEAD)
            print(head_string)
            body_string = ''.join(BODY)
            forbidden_list = data["forbidden_words"]
            for i in forbidden_list:
                word = list(i.keys())[0]
                if word in body_string:
                    body_string = body_string.replace(word,i[word])

            """ dict = list(response.headers.keys())
            HEAD = ""
            HEAD += (http_string.split(" ", 2)[2].split("\r\n", 1))[0].replace(" ", "")
            HEAD += " " + str(response.status_code) + " " + response.reason + "\r\n"
            for keys in dict:
                HEAD += keys + ": " + response.headers[keys] + "\r\n" """
            head_string = head_string[:-2]
            head_string += "X-ElQuePregunta: "+name_user+"\r\n\r\n" 
            HTTP = head_string + body_string
            return HTTP



buff_size = 50
end_of_head = "\r\n\r\n"
new_socket_address = ('localhost', 8001)

print('Creando socket - Proxy')

proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

proxy_socket.bind(new_socket_address)

proxy_socket.listen(3)

print('... Esperando clientes')
while True:
    new_socket, new_socket_address = proxy_socket.accept()
    recv_http= receive_http(new_socket, buff_size, end_of_head)

    print('Se ha recibido el HTTP')

    response = send_http(recv_http)
    new_socket.send(response.encode())

    print('Se ha recibido la response')

    new_socket.close()
    print(f"conexión con {new_socket_address} ha sido cerrada")
