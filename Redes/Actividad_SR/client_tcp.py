from socketTCP import socketTCP
import socket

# CLIENT
# Mensje de len=16Mensje de len=16
# Mensaje de largo 19Mensaje de largo 19

client_socketTCP = socketTCP()
client_socketTCP.set_buffSize(3)
client_socketTCP.set_address(('localhost', 8010))
client_socketTCP.connect(('localhost', 8010))
client_socketTCP.set_timeout(5)

# test 1
client_socketTCP.send()

# test 2
client_socketTCP.send()

""" # test 3
client_socketTCP.send() """

client_socketTCP.close()