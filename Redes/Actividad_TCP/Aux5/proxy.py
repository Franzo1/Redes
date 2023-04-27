import socket

# Fin de línea para headers
header_end = b'\r\n'

class proxy:
  """
  Clase que implementa el funcionamiento de un proxy,
  según lo explicitado en la actividad 1.
  """

  def __init__(self, address, buff_size, json) -> None:
    """
    Clase que implementa el funcionamiento de un proxy,
    según lo explicitado en la actividad 1.

    Parameters
    ----------
    address : tuple[str, int]
      Dirección del socket utilizado para recibir clientes.
    buff_size : int
      Tamaño del buffer size a utilizar en los sockets.
    json : dict
      Diccionario leído desde archivo json, que entrega parámetros
      a utilizar por el proxy.
    """
    self.address = address      # Dirección del socket que se utilizará para recibir clientes
    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Socket para recibir clientes
    self.bind()                 # Se llama a la función para bindear el socket a su dirección
    self.buff_size = buff_size  # Tamaño de los buffer a utilizar en las conexiones
    self.json_dict = json       # Diccionario leído desde archivo json

  def bind(self) -> None:
    """
    Bindear el socket del proxy a la direccion en la cual escuchar
    """
    self.socket.bind(self.address)
    self.socket.listen()

  def accept(self) -> tuple[socket.socket, tuple[str, int]]:
    """
    Aceptar la conexión de cliente entrante y retornar la
    tupla NuevoSocket, DirecciónCliente
    """
    return self.socket.accept()

  # Hacer un método estático, significa que no es necesario instanciar
  # un objeto para llamarlo.
  # Se puede utilizar con proxy.parse_headers()
  @staticmethod
  def parse_headers(headers) -> dict:
    """
    Parsear mensaje a headers. Lo trabajamos en bytes
    """
    headers_split = headers.split(header_end)
    headers_dict = {b'first': headers_split.pop(0)}
    # Recorremos el arreglo de headers para guardarlo en el diccionario creado
    for header in headers_split:
      key, value = header.split(b": ")
      headers_dict[key] = value
    # Retornamos diccionario
    return headers_dict

  @staticmethod
  def dict_to_header(headers_dict) -> bytes:
    """
    Diccionario headers a bytes
    """
    # Debido a que la primera linea es diferente, la extraemos a mano
    # y la omitimos en la recursión
    headers = headers_dict.pop(b'first') + header_end
    # Iterar por las llaves del diccioario
    for header in headers_dict:
      headers += header + b': ' + headers_dict[header] + header_end
    return headers+header_end

  def recv_client_message(self, socket) -> dict:
    """
    Recibir mensaje desde cliente y toma decisiones al respecto.
    Retorna el diccionario con los headers respectivos.
    """
    encoded = b''
    # Se recibe el mensaje por pedazos
    while 2*header_end not in encoded:
      encoded += socket.recv(self.buff_size)
    # Se parsea el diccionario
    headers_dictionary = proxy.parse_headers(encoded[:-2*len(header_end)])
    # Se verifica que la dirección (host + path) no esté bloqueada
    # No siempre la start line viene con todo el url, a veces solo viene el path
    # Por lo que sería bueno que lo verificaran
    if (headers_dictionary[b'first'].split()[1].decode() in self.json_dict['blocked']):
      headers_dictionary[b'first'] = b'HTTP/1.1 403 Forbidden'
      return headers_dictionary
    # Añadir header custom
    headers_dictionary[b'X-ElQuePregunta'] = self.json_dict['user'].encode()
    return headers_dictionary

  def send_message_to_server(self, message, host) -> bytes:
    """
    Enviar mensaje hacia el servidor, se recibe su respuesta
    y se toma decisión al respecto.
    """
    # Se crea un nuevo socket que se conecta al server
    socket_to_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_to_server.connect((host, 80))
    socket_to_server.send(message)

    server_response = b''
    while 2*header_end not in server_response:
      server_response += socket_to_server.recv(self.buff_size)

    # Hacer split de headers y body.
    # Si lanza error, significa que el tamaño del buffer era justo
    # para recibir los headers, por lo que solo se guardan los headers
    # y el body se inicializa vacío
    try:
      headers, body = server_response.split(2*header_end)
    except ValueError:
      headers = server_response[:-2*len(header_end)]
      body = b''
    # Parsear headers
    headers_dict = self.parse_headers(headers)

    # Se lee el content-length para recibir por pedazos
    while len(body) < int(headers_dict[b'Content-Length']):
      body += socket_to_server.recv(self.buff_size)
    socket_to_server.close()

    # Se reemplazan las palabras y se calcula el nuevo largo del body
    body_replaced, contentlength = self.replace_words(body)
    headers_dict[b'Content-Length'] = contentlength
    # Se transforman el diccionario a bytes
    new_headers = self.dict_to_header(headers_dict)
    # Se rearma todo el mensaje del server, con los cambios del proxy
    return new_headers + body_replaced

  @staticmethod
  def error_page(headers_dictionary, body) -> bytes:
    """
    Respuesta error, simplemente arma la página de error
    """
    headers_dictionary[b'Content-Length'] = str(len(body.encode())).encode()
    headers = proxy.dict_to_header(headers_dictionary)
    return headers + body.encode()

  def replace_words(self, body) -> tuple[bytes, int]:
    """
    Reemplazar palabras en body, según lo dictado por el diccionario json
    """
    body_decoded = body.decode()
    for word in self.json_dict['forbidden_words']:
      body_decoded = body_decoded.replace(word, self.json_dict['forbidden_words'][word])
    body_encoded = body_decoded.encode()
    return body_encoded, str(len(body_encoded)).encode()