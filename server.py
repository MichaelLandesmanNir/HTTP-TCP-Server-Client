import socket
import os
import sys

# Directory containing the files to be served
DIR = 'files'
# Buffer size for receiving data
BUFFER_SIZE = 4064

def find_connection_type(header_lines):
    """
    Extracts the connection type from the HTTP request headers.

    :param header_lines: List of HTTP header lines
    :return: Connection type (e.g., 'keep-alive' or 'close'), or None if not found
    """
    for line in header_lines:
        if line.lower().startswith("connection:"):
            connection_type = line.split(":", 1)[1].strip()
            return connection_type
    return None

def read_file(file_path):
    """
    Reads the content of a file and returns it as bytes.

    :param file_path: The path to the requested file
    :return: File content in bytes
    """
    if file_path.endswith(('.jpg', '.ico')):  # Binary files (images, icons)
        with open(file_path, "rb") as file:
            return file.read()
    else:  # Text files (HTML, CSS, etc.)
        with open(file_path, "r") as file:
            return file.read().encode()

def main(port):
    """
    Starts a simple HTTP server that listens for incoming connections.

    :param port: The port number the server will listen on
    """


    # Create a TCP socket for the server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the specified port and listen on all available interfaces
    server_socket.bind(('', port))
    # Listen for incoming connections (maximum queue of 5 clients)
    server_socket.listen(5)

    while True:
        try:
            # Accept a new client connection
            client_socket, addr = server_socket.accept()
            client_socket.settimeout(1)
            # Buffer for accumulating received data

            buffer = ""  
            connection_alive = True  # Track if connection should remain open

            while connection_alive:
                data = client_socket.recv(BUFFER_SIZE)
                if not data:
                    break

                data = data.decode("utf8")
                buffer += data

                # Check if the full HTTP request has been received
                if '\r\n\r\n' in buffer:
                    # Extract request headers
                    header = buffer.split('\r\n\r\n')[0]
                    header_lines = header.split('\r\n')
                    header_request_line = header_lines[0]

                    # Extract the requested file path
                    path = header_request_line.split(" ")[1]
                    connection_type = find_connection_type(header_lines)
                    file_path = ""

                    # Ensure path starts with "/"
                    if not path.startswith("/"):
                        path = '/' + path

                    if path == '/':
                        # Serve the default index page
                        file_path = DIR + '/index.html'
                    elif path == '/redirect':
                        file_path = '/result.html'
                    else:
                        path = DIR + path
                        if os.path.exists(path) and not os.path.isdir(path):
                            file_path = path

                    # Handle redirection response
                    if file_path == '/result.html':
                        connection_type = 'close'
                        response_header = 'HTTP/1.1 301 Moved Permanently\r\n'
                        response_header += f'Connection: {connection_type}\r\n'
                        response_header += 'Location: /result.html\r\n\r\n'
                        client_socket.sendall(response_header.encode('utf-8'))
                        

                    # Handle file not found (404 error)
                    elif not file_path:
                        connection_type = 'close'
                        response_header = 'HTTP/1.1 404 Not Found\r\n'
                        response_header += 'Connection: close\r\n\r\n'
                        client_socket.sendall(response_header.encode('utf-8'))
                        connection_alive = False

                    # Serve the requested file
                    else:
                        response_data = read_file(file_path)
                        len_file_content = len(response_data)
                        response_header = 'HTTP/1.1 200 OK\r\n'
                        response_header += f'Connection: {connection_type}\r\n'
                        response_header += f'Content-Length: {len_file_content}\r\n\r\n'

                        client_socket.sendall(response_header.encode('utf-8'))
                        client_socket.sendall(response_data)

                    buffer = ''
                    if connection_type == 'close':
                        connection_alive = False

        except socket.timeout:
            pass  # Ignore timeout errors
        finally:
            client_socket.close()  # Ensure client socket is closed

if __name__ == "__main__":
    # Ensure the correct number of command-line arguments
    if len(sys.argv) != 2:
        print("Usage: python server.py <port>")
        sys.exit(1)

    TCP_PORT = int(sys.argv[1])
    main(TCP_PORT)
