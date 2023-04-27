from socketTCP import socketTCP
import socket

# SERVER
""" serverSocket = socketTCP()
serverSocket.set_address(('localhost', 8000))
serverSocket.bind() """

server_socketTCP = socketTCP()
server_socketTCP.set_address(('localhost', 8000))
server_socketTCP.set_buffSize(18)
server_socketTCP.bind()
connection_socketTCP, new_address = server_socketTCP.accept()

""" # test 1
serverSocket.set_buffSize(16)
full_message, newAddress = serverSocket.receive_in_bytes()
print("Test 1 received:", full_message)
if full_message == "Mensje de len=16".encode(): print("Test 1: Passed")
else: print("Test 1: Failed")

# test 2
serverSocket.set_buffSize(19)
full_message, newAddress = serverSocket.receive_in_bytes()
print("Test 2 received:", full_message)
if full_message == "Mensaje de largo 19".encode(): print("Test 2: Passed")
else: print("Test 2: Failed")

# test 3
serverSocket.set_buffSize(14)
message_part_1, newAddress = serverSocket.receive_in_bytes()
message_part_2, newAddress = serverSocket.receive_in_bytes()
print("Test 3 received:", message_part_1 + message_part_2)
if (message_part_1 + message_part_2) == "Mensaje de largo 19".encode(): print("Test 3: Passed")
else: print("Test 3: Failed") """