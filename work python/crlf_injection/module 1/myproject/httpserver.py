"""
Implements a simple HTTP/1.0 Server
Based on https://gist.githubusercontent.com/joaoventura/824cbb501b8585f7c61bd54fec42f08f/raw/dbd18e3b50feb7be3fe2e12481ec7731ef71050d/httpserver.py
"""

import socket
import os
from urllib.parse import unquote

CRLF = "\r\n"
DEBUG = True

def handle_request(request,client_address):
    """Handles the HTTP request."""

    headers = request.split(CRLF)
    
    filename = headers[0].split()[1][1:] # /index.html --> index.html
    filename = unquote(filename) # Decode URL: index%2ehtml --> index.html

    GET_PARAMS = ""

    if '?' in filename: # Có GET Parameter
        GET_PARAMS = filename.split('?')[1] # index.html?param=1 --> param=1
        filename = filename.split('?')[0] # index.html?param=1 --> index.html

    if filename == '':
        filename = 'index.html'

    # Lấy language từ GET PARAMS
    if 'lang=' in GET_PARAMS:
        language = GET_PARAMS.split("lang=")[1] # index.html?lang=vietnamese --> vietnamese
    else:
        # Mặc định là tiếng Anh 
        language = "english" 

    if language == "vietnamese" and filename == "index.html":
        # Nếu ngôn ngữ là Vietnamese thì index.html sẽ chuyển sang index.vi.html
        filename = "index.vi.html" 
    

    # Tạo ra các trường HTTP response trả về cho client
    response_headers = CRLF.join([
        "Content-Type: text/html",
        "Set-Cookie: lang={}".format(language)
    ])
    

    try:
        # Tìm kiếm file trong DocumentRoot
        abs_filename = os.path.join(".","documentroot",filename)
        fin = open(abs_filename)
        content = fin.read()
        fin.close()

        if DEBUG == True:# Bật Debug để có thể thấy ruột của gói tin 
            debug_log = response_headers+CRLF+CRLF
            debug_log = debug_log.replace('<','&lt;').replace('>','&gt;') # XSS ESCAPE :(

            content += "<br><h3>DEBUG LOG (HTTP RESPONSE)</h3><pre id=debug>{}</pre>".format(
                debug_log.replace("\r\n","\\r\\n\r\n") # Highlight cho dễ nhìn CRLF
            )

        # Tạo gói tin HTTP hoàn chỉnh để trả về
        response = """HTTP/1.0 200 OK{}{}{}{}""".format(
            CRLF,
            response_headers,
            CRLF+CRLF,
            content
        )

    except (FileNotFoundError, Exception) as e:
        # Không tìm thấy file
        response = """HTTP/1.0 404 NOT FOUND{}{}{}{}""".format(
            CRLF,
            response_headers,
            CRLF+CRLF,
            "File not found"
        )

    return response


# Define socket host and port
SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8080

# Create socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((SERVER_HOST, SERVER_PORT))
server_socket.listen(1)
while True:
    # Wait for client connections
    client_connection, client_address = server_socket.accept()

    # Get the client request
    request = client_connection.recv(1024).decode()

    # Return an HTTP response
    response = handle_request(request,client_address)
    client_connection.sendall(response.encode())

    # Close connection
    client_connection.close()

# Close socket
server_socket.close()