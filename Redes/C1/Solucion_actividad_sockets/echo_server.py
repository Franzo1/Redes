import socket
# importamos utils completo
from utils import *

print('Creando socket - Servidor')
# armamos el socket no orientado a conexión
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# definimos dirección donde queremos que correr el server_socket
server_address = ('localhost', 5000)

# hacemos bind del server socket a la dirección server_address
server_socket.bind(server_address)

# nos quedamos esperando, como buen server, a que llegue una petición de conexión
print('... Esperando clientes')
while True:
    # luego recibimos el mensaje usando la función receive_full_mesage en su version no orientada a conexión
    received_message, server_address = receive_full_mesage(server_socket, buff_size_server, end_of_message)

    print(f" -> Se ha recibido el siguiente mensaje: {received_message.decode()}")

    # respondemos lo mismo y le volvemos a añadir el end_of_message
    response_message = received_message + end_of_message.encode()

    # re-enviamos el mensaje de vuelta al cliente, desired_message_loss indica el porcentaje de perdida que queremos inducir
    desired_message_loss = 20
    send_full_message(server_socket, response_message, end_of_message, server_address, buff_size_client, message_loss_percentage=desired_message_loss)
    print("Se ha hecho eco del mensaje")

    # seguimos esperando por si llegan otras conexiones
