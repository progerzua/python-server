# nuages - through
# dream dama - without you

''' TODO:
* add serving of separate files
'''
import socket
from os import listdir
from os.path import isfile, join, realpath, dirname
import sys

def scan_index(path):

    '''
    This function search for index.html in folder, located at path.
    If path emtpy - it search in the root.
    '''

    dir_path = dirname(realpath(__file__)) + path

    for f in listdir(dir_path):
        if isfile(join(dir_path, f)) and f == "index.html":
            return True

    return False

def scandir(path):

    dir_path = dirname(realpath(__file__)) + path
    directories = []
    files = []
    for f in listdir(dir_path):
        if isfile(join(dir_path, f)):
            files.append(f)
        else:
            directories.append(f)
    return directories, files

def generate_response(dirs, files, path):
    answer = b'''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
    <html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Directory listing for ''' + str.encode(path) + b'''</title>
    </head>
    <body>
    <h1>Directory listing for /</h1>
    <hr>'''

    # That version even better than original - it shows folders first
    if dirs or files:
        answer += b'<ul>'
        for i in dirs:
            answer += b'<li><a href="' + str.encode(i) + b'/">'+ str.encode(i) + b'/</a></li>'
        for i in files:
            answer += b'<li><a href="' + str.encode(i) + b'">'+ str.encode(i) + b'</a></li>'
    answer += b'</ul><hr></body></html>'

    return answer

def main():
    HOST = ''
    PORT = 80
    server = b"\nServer: NativePy/0.1b"

    # Init connection
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        listen_socket.bind((HOST, PORT))
    except socket.error as msg:
        print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    print('Bind succeed')
    listen_socket.listen(5)
    print('Serving HTTP on port %s ...' % PORT)

    while True:

        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(1024)
        print("Conected with ", client_address)
        request_line = [i.strip() for i in request.splitlines()][0]
        method,req_path,req_version = request_line.split()
        body = b''

        if (method == b'GET'):
            path = '' if req_path == b'/' else req_path.decode("utf-8")
            if(scan_index(path)):
                body = str.encode((open(join(dirname(realpath(__file__)) + path, 'index.html'), 'r')).read())
                content_type = b"\nContent-type: text/html; charset=utf-8"
                content_length = b"\nContent-Length: " + str.encode(str(len(body)))
                HEADERS = b"HTTP/1.1 200 OK" + server + content_type + content_length
            else:
                dirs, files = scandir(path)
                body = generate_response(dirs,files, path)
                HEADERS = b""

        http_response = HEADERS + b"\r\n\r\n" + body
        client_connection.sendall(http_response)
        client_connection.close()

if __name__ == "__main__":
    main()
