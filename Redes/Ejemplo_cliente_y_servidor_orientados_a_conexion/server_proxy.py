import socket


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


def send_http(connection_socket, head_list, body_list):
    http_string = ''.join(head_list) + ''.join(body_list)
    connection_socket.send(http_string.encode())


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
    recv_head, recv_body = receive_http(new_socket, buff_size, end_of_head)

    print('Se ha recibido el HTTP')

    send_http(new_socket, recv_head, recv_body)

    print('Se ha recibido la response')

    new_socket.close()
    print(f"conexión con {new_socket_address} ha sido cerrada")
