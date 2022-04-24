"""
This module is a demonstration of how to send
a HTTP request from scratch with the socket module.
"""
import socket
import re
import base64

"""
The term CRLF refers to Carriage Return (ASCII 13, \r)
Line Feed (ASCII 10, \n).
They're used to note the termination of a line,
however, dealt with
differently in today's popular Operating Systems.
"""
CRLF = '\r\n'
SP = ' '
CR = '\r'
HOST = 'www.example.com'
PORT = 80
PATH = '/'


def DEBUG_LOG(log):
    global debug_log
    log = log.replace("\r\n","\\r\\n\r\n")
    debug_log += log+"\n"

def send_request(host=HOST, path=PATH, port=PORT, user_agent=None):
    DEBUG_LOG("[DEBUG] Connecting to host: {} (port: {})".format(repr(host),repr(port)))
    sock = socket.socket()
    sock.settimeout(5.0)
    # Connect to the server.
    sock.connect((host, port))

    headers_ = ["User-Agent: {}".format(user_agent)]
    # Send the request, crafting raw HTTP request packet
    payload_request = CRLF.join([
        "GET {} HTTP/1.1".format(path),
        "Host: {}".format(host),
        *headers_,
        "Connection: Close\r\n\r\n"
    ])

    # DEBUG
    DEBUG_LOG("\n\n>>>>>>>>> HTTP REQUEST")
    DEBUG_LOG(payload_request)

    sock.send(payload_request.encode())
    # Get the response.
    response = bytes()
    chuncks = sock.recv(4096)
    while chuncks:
        response += chuncks
        chuncks = sock.recv(4096)

    # DEBUG
    DEBUG_LOG("<<<<<<<<< HTTP RESPONSE")
    DEBUG_LOG(response.decode('ISO-8859-1'))

    # HTTP headers will be separated from the body by an empty line
    header, _, body = response.partition(CRLF.encode()*2)

    # return header, code, body
    return header, body


_hostprog = None
def _splithost(url):
    """splithost('//host[:port]/path') --> 'host[:port]', '/path'."""
    global _hostprog
    if _hostprog is None:
        _hostprog = re.compile('//([^/#?]*)(.*)', re.DOTALL)

    match = _hostprog.match(url)
    if match:
        host_port, path = match.groups()
        if path and path[0] != '/':
            path = '/' + path
        return host_port, path
    return None, url

_portprog = None
def _splitport(host):
    """splitport('host:port') --> 'host', 'port'."""
    global _portprog
    if _portprog is None:
        _portprog = re.compile('(.*):([0-9]*)$', re.DOTALL)

    match = _portprog.match(host)
    if match:
        host, port = match.groups()
        if port:
            return host, port
    return host, None


def do_fetch_image(url,user_agent_):
    global debug_log
    
    debug_log = ''
    response_text = bytes()

    if user_agent_ == None:
        user_agent_ = "this_is_my_own_http_library"

    if url.startswith('http://'):
        url = url[5:]
        host_, path_ = _splithost(url)
        host_, port_ = _splitport(host_)
        DEBUG_LOG("[DEBUG] Host: {}".format(host_))
        DEBUG_LOG("[DEBUG] Path: {}".format(path_))
        DEBUG_LOG("[DEBUG] Port: {}".format(port_))
        DEBUG_LOG("[DEBUG] User-Agent: {}".format(user_agent_))

        header,  body  = send_request(
            host=host_,
            path=path_,
            port=80 if port_ == None else int(port_),
            user_agent=user_agent_
        )

        response_text = base64.b64encode(body)
    else:
        return False

    return {'debug':debug_log, "image_encoded": response_text.decode()}
