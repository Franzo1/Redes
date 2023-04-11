import socket
# importamos utils completo
from utils import *

# creamos el socket cliente (no orientado a conexión)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# definimos el path donde se encuentra el archivo que queremos enviar
path = "texto.txt"

# abrimos el archivo y lo leemos
file = open(path, 'r')
message = file.read()

# le agregamos la secuencia de fin de mensaje
message_with_end_sequence = message + end_of_message

# enviamos el mensaje usando send_full_message para asegurarse que el mensaje se envíe por trozos
# desired_message_loss indica el porcentaje de perdida que queremos inducir
destination_address = ('localhost', 5000)
desired_message_loss = 0
send_full_message(client_socket, message_with_end_sequence.encode(), end_of_message, destination_address, buff_size_server, message_loss_percentage=desired_message_loss)

print(f"Se ha enviado el mensaje contenido en: {path}")

# luego de enviar el mensaje esperamos el eco
received_message, destination_address = receive_full_mesage(client_socket, buff_size_client, end_of_message)

print(f"Se ha recibido desde servidor echo: {received_message.decode()}")

# Si los mensajes son distintos entonces hubo pérdida

if received_message.decode() != message:
    print("\n--------> Hubo pérdida, los mensajes no son iguales!")

else:
    print("\n--------> los mensajes son iguales :D")