from socketTCP import socketTCP
import socket

# CLIENT

client_socketTCP = socketTCP()
client_socketTCP.set_buffSize(3)
client_socketTCP.connect(('localhost', 8000))

# test 1
client_socketTCP.send("selective_repeat")

# test 2
client_socketTCP.send("selective_repeat")

""" # test 3
client_socketTCP.send() """

client_socketTCP.close()