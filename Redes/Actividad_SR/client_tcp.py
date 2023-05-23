from socketTCP import socketTCP
import socket

# CLIENT
# Mensje de len=16Mensje de len=16

client_socketTCP = socketTCP()
client_socketTCP.set_buffSize(3)
client_socketTCP.connect(('localhost', 8000))
client_socketTCP.set_timeout(5)

# test 1
client_socketTCP.send("selective_repeat")

# test 2
client_socketTCP.send("selective_repeat")

""" # test 3
client_socketTCP.send() """

client_socketTCP.close()