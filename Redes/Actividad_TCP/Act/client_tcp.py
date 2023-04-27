from socketTCP import socketTCP
import socket

# CLIENT
""" clientSocket = socketTCP()
clientSocket.set_otherAddress(('localhost', 8000))
clientSocket.set_buffSize(16) """

client_socketTCP = socketTCP()
client_socketTCP.set_buffSize(18)
client_socketTCP.connect(('localhost', 8000))

""" # test 1
clientSocket.set_message()
clientSocket.send_in_bytes()

# test 2
clientSocket.set_message()
clientSocket.send_in_bytes()

# test 3
clientSocket.set_message()
clientSocket.send_in_bytes() """