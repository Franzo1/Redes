from socketTCP import socketTCP
import socket

# CLIENT
# Mensje de len=16
# Mensaje de largo 19

client_socketTCP = socketTCP()
client_socketTCP.set_buffSize(3)
client_socketTCP.set_address(('localhost', 8005))
client_socketTCP.connect(('localhost', 8005))
client_socketTCP.set_timeout(5)
client_socketTCP.set_window_size(10)

# test 1
client_socketTCP.send("selective_repeat")

# test 2
client_socketTCP.send("selective_repeat")

# test 3
client_socketTCP.send("selective_repeat")

client_socketTCP.close()