from socketTCP import socketTCP
import socket

# CLIENT

client_socketTCP = socketTCP()
client_socketTCP.set_buffSize(16)
client_socketTCP.connect(('localhost', 8000))

# test 1
client_socketTCP.set_message()
client_socketTCP.send()

# test 2
client_socketTCP.set_message()
client_socketTCP.send()

# test 3
client_socketTCP.set_message()
client_socketTCP.send()

client_socketTCP.close()