import socket
import sys
import os

# Directory where downloaded files will be saved
DIR = 'files'

def save_file(file_name, response_data):
    """
    Saves the received response data to a file.

    :param file_name: The name of the file to save
    :param response_data: The content to be written into the file
    """
    if file_name.endswith(('.jpg', '.ico')):  # Save binary files
        #print("file_name.endswith(('.jpg', '.ico')):")
        with open(file_name, 'wb') as file:
            return file.write(response_data)
    else:  
        
        with open(file_name, 'w') as file:
            return file.write(response_data.decode())

def main():
    """
    Starts the client, connects to the server, sends HTTP requests, 
    and processes responses.
    """
    BUFFER_SIZE = 4096  
    server_ip = sys.argv[1] 
    server_port = int(sys.argv[2])  # Get server port from command-line argument
    # Variable to store redirected paths
    server_input = ''  

    # Infinite loop to allow multiple file requests
    while True:
        # Use saved server input if available, otherwise prompt user input
        if server_input:
            file_path = server_input
            server_input = ''
        else:
            file_path = input()  # Get file path from user input
        
        if file_path == '':
            file_path = '/'  # Default to root if no input is provided

        # Construct HTTP GET request
        request = f"GET {file_path} HTTP/1.1\r\nConnection: open\r\n\r\n"
       
        # Create and connect a new socket to the server
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((server_ip, server_port))
        client_socket.sendall(request.encode('utf-8'))

        # Initialize buffer to store response data
        buffer = b''
        while b"\r\n\r\n" not in buffer:
            chunk = client_socket.recv(BUFFER_SIZE)
            if not chunk:
                break
            buffer += chunk  # Append received data to buffer
        
        # Split response into headers and body
        header, _, response_data = buffer.partition(b"\r\n\r\n")
        header = header.decode(errors='ignore')
        response_list = header.split("\r\n")
        
        # Extract status code from response headers
        first_line_header = response_list[0]
        response_code_num = int(first_line_header.split(" ")[1])

        # Extract content length (if exists) and fetch remaining response data
        length_response_data = None
        for line in response_list:
            if line.lower().startswith("content-length:"):
                length_response_data = int(line.split(":")[1].strip())

        if length_response_data:
            while len(response_data) < length_response_data:
                chunk = client_socket.recv(BUFFER_SIZE)
                if not chunk:
                    break
                response_data += chunk

        # Handle redirection if "Location" header is present
        location = None
        for line in response_list:
            if line.lower().startswith("location:"):
                location = line.split(": ")[1].strip()

        print(first_line_header)  # Print response status line
        
        # Process response based on status code
        if response_code_num == 200:
            # Determine file name to save
            if file_path == "/":
                file_name = 'index.html'
            else:
                #print(f"file path= {file_path}")
                file_name = os.path.basename(file_path)
                #print(f"file name= {file_name}")
            save_file(file_name=file_name, response_data=response_data)
        
        
        elif response_code_num == 301: 
            if location:
                # Handle redirection by setting new input path
                server_input = location.replace("files", "")

        client_socket.close()  # Close the client socket

if __name__ == "__main__":
    # Ensure correct command-line arguments
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_ip> <server_port>")
        sys.exit(1)
    main()
