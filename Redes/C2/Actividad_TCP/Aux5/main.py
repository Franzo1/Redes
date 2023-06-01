import sys, json
from proxy import proxy

"""
Se abren y leen archivos
"""
# Abrir diccionario json
with open(sys.argv[1], 'r') as f:
    json_file = f.read()
f.close()
json_file = json.loads(json_file)
# Leer página de error
with open('error.html') as file:
  error_html_body = file.read()

# Se instancia un proxy
proxy_server = proxy(('localhost', 8000), 40, json_file)
print('Se creó el proxy.')

# Se encierra en try except, para cerrarlo bonitamente cuando se haga ctrl+c
try:
# Loop principal
  while True:
    print('Se espera conexión de un cliente.\n')
    # Se recibe request del cliente de iniciar conexión
    new_socket, client_address = proxy_server.accept()
    # Se recibe request del cliente
    print('Se recibe request del cliente.')
    received_dictionary = proxy_server.recv_client_message(new_socket)
    # Si es página bloqueada, armar página de error
    if (received_dictionary[b'first'] == b'HTTP/1.1 403 Forbidden'):
      print('Cliente pidió por página prohibida.')
      server_response = proxy.error_page(received_dictionary, error_html_body)
    # Si no, se envía al server para luego obtener su respuesta
    else:
      print('Se envía request a servidor y se recibe su respuesta.')
      server_response = proxy_server.send_message_to_server(proxy_server.dict_to_header(received_dictionary), received_dictionary[b'Host'])
    # Se envía respuesta al cliente
    print('Se envía respuesta a cliente.\n')
    new_socket.send(server_response)
except KeyboardInterrupt:
  print('\rPrograma finalizado por usuario.')
