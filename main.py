# Not the best piece of code
# Some parts written in deep night =)

import socket
from os import listdir
from os.path import isfile, join, realpath, dirname, exists, basename
import sys
import datetime  # To show time, when client connected, like in original module


def scan_index(path):
    """

    This function search for index.html in folder, located at path.
    If path emtpy - it search in the root.

    """
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
    #foldername = path.split("/")[-1] if path.split("/")[-1] != '' else path.split("/")[-2]
    if path == "":
        foldername = b""
    else:
        foldername = str.encode(basename(dirname(dirname(realpath(__file__)) + path)))

    answer = b'''
    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
    "http://www.w3.org/TR/html4/strict.dtd">
    <html>
    <head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>Directory listing for ''' + foldername + b'''</title>
    </head>
    <body>
    <h1>Directory listing for /''' + foldername + b'''</h1>
    <hr>'''

    # That version even better than original - it shows folders first
    if dirs or files:
        answer += b'<ul>'
        for i in dirs:
            answer += b'<li><a href="' + str.encode(i) + b'/">' + str.encode(i) + b'/</a></li>'
        for i in files:
            answer += b'<li><a href="' + str.encode(i) + b'">' + str.encode(i) + b'</a></li>'
    answer += b'</ul><hr></body></html>'

    return answer

def serve_file(path):
    extension = (path.split('/'))[-1].split('.')[-1]
    ext_dict = {
        "js": b"application/javascript",
        "json": b"application/json",
        "xml": b"application/xml",
        "zip": b"application/zip",
        "pdf": b"application/pdf",
        "css": b"text/css",
        "html": b"text/html; charset=utf-8",
        "txt": b"text/plain; charset=utf-8",
        "png": b"image/png",
        "jpg": b"image/jpeg",
        "gif": b"image/gif",
    }
    if extension in ext_dict:
        f = open(dirname(realpath(__file__)) + path, "rb")
        body = f.read()
        f.close()
        content_type = b"\nContent-type: " + ext_dict[extension]
    else:
        content_type = b"\nContent-type: application/octet-stream"
    f = open(dirname(realpath(__file__)) + path, "rb")
    body = f.read()
    content_length = b"\nContent-Length: " + str.encode(str(len(body)))
    f.close()
    return content_type, content_length, body


def main():
    HOST = ''
    PORT = 80  # by Default
    if(len(sys.argv) > 1):
        PORT = int(sys.argv[-1]) if sys.argv[-1].isdigit() else 80
    server = b"\nServer: SimpleHTTP-clone/0.1b"

    # Init connection
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        listen_socket.bind((HOST, PORT))
    except socket.error as msg:
        print ('Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.exit()
    listen_socket.listen(5)
    print('Serving HTTP on port %s ...' % PORT)

    while True:

        client_connection, client_address = listen_socket.accept()
        request = client_connection.recv(1024)
        # TndexError appear below sometimes O_ o
        # If you wait for some time, for example
        # Have no time to check. Added rude exception, sorry
        try:
            request_line = [i.strip() for i in request.splitlines()][0]
        except:
            request_line = b'GET / HTTP/1.1'
        method, req_path, req_version = request_line.split()

        body = b''

        if (method == b'GET'):
            if req_path == b'/':
                path = ''
                isfolder = True
                valid_path = True
            else:
                path = req_path.decode("utf-8")
                valid_path = True if exists(dirname(realpath(__file__)) + path) else False
                isfolder = False if isfile(dirname(realpath(__file__)) + path) else True
            if(isfolder and valid_path and scan_index(path)):
                body = str.encode((open(join(dirname(realpath(__file__)) + path, 'index.html'), 'r')).read())

                content_type = b"\nContent-type: text/html; charset=utf-8"
                content_length = b"\nContent-Length: " + str.encode(str(len(body)))
                status = b"HTTP/1.1 200 OK"
            elif(isfolder and valid_path):
                dirs, files = scandir(path)
                body = generate_response(dirs, files, path)

                content_type = b"\nContent-type: text/html; charset=utf-8"
                content_length = b"\nContent-Length: " + str.encode(str(len(body)))
                status = b"HTTP/1.1 200 OK"
            elif(valid_path and not isfolder):
                content_type, content_length, body = serve_file(path)
                status = b"HTTP/1.1 200 OK"
            elif(not valid_path):
                body = b'''
                    <!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
                            "http://www.w3.org/TR/html4/strict.dtd">
                    <html>
                        <head>
                            <meta http-equiv="Content-Type" content="text/html;charset=utf-8">
                            <title>Error response</title>
                        </head>
                        <body>
                            <h1>Error response</h1>
                            <p>Error code: 404</p>
                            <p>Message: File not found.</p>
                            <p>Error code explanation: HTTPStatus.NOT_FOUND - Nothing matches the given URI.</p>
                        </body>
                    </html>'''

                content_type = b"\nContent-type: text/html; charset=utf-8"
                content_length = b"\nContent-Length: " + str.encode(str(len(body)))
                status = b"HTTP/1.1 404 Not Found"
        HEADERS = status + server + content_type + content_length
        http_response = HEADERS + b"\r\n\r\n" + body
        client_connection.sendall(http_response)
        client_connection.close()

        d = datetime.datetime.now()
        curdate = d.strftime("%d/%b/%Y %H:%M:%S")
        print(client_address[0] + " - - [" + curdate + "] \"" + request_line.decode("utf-8") + "\" " + status.decode("utf-8"))


if __name__ == "__main__":
    main()
