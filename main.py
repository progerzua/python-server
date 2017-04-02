import socket

HOST = ''
PORT = 80

listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
try:
    listen_socket.bind((HOST, PORT))
except socket.error as msg:
    print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
    sys.exit()
print('Bind succeed')
listen_socket.listen(5)
print('Socket listening')
print('Serving HTTP on port %s ...' % PORT)
while True:
    client_connection, client_address = listen_socket.accept()
    request = client_connection.recv(1024)
    print("Conected with ", client_address)
    # print(request)
    splitted_request = [i.strip() for i in request.splitlines()]
    requested_url = temp[0]

    http_response = b"""\
HTTP/1.1 200 OK

You`re awesome!
"""
    client_connection.sendall(http_response)
    client_connection.close()
