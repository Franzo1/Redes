from socketTCP import socketTCP
import socket

# SERVER

server_socketTCP = socketTCP()
server_socketTCP.set_address(('localhost', 8000))
server_socketTCP.set_buffSize(18)
server_socketTCP.bind()
connection_socketTCP, new_address = server_socketTCP.accept()

# test 1
connection_socketTCP.set_buffSize(3)
full_message, newAddress = connection_socketTCP.recv()
print("Test 1 received:", full_message)
if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
else: print("Test 1: Failed")

# test 2
connection_socketTCP.set_buffSize(3)
full_message, newAddress = connection_socketTCP.recv()
print("Test 2 received:", full_message)
if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
else: print("Test 2: Failed")

""" # test 3
connection_socketTCP.set_buffSize(3)
message_part_1, newAddress = connection_socketTCP.recv()
message_part_2, newAddress = connection_socketTCP.recv()
print("Test 3 received:", message_part_1 + message_part_2)
if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): print("Test 3: Passed")
else: print("Test 3: Failed") """