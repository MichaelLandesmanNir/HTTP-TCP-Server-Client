## HTTP Server base TCP
# Project Overview
This project implements a simplified HTTP server in Python, capable of handling GET requests for static content such as HTML files, images, and redirects. Additionally, a client program is included to test the server’s functionalities, including persistent connections and automatic reconnections. The project showcases fundamental networking principles, such as socket communication, request interpretation, and response construction in a web environment.

---

# Client
The client is designed to send HTTP GET requests to the server and supports persistent connections, allowing multiple requests to be sent over a single connection. It also includes mechanisms to detect and recover from connection failures.

# Key Features:

- Sends HTTP GET requests to a given server address and port.
- Supports Connection: keep-alive to maintain persistent connections.
- Detects connection drops and automatically reconnects, resending the last 
  request when needed.

# Server
The server listens for incoming HTTP requests and serves files from a specified directory. It also manages errors like missing files and redirections.

# Key Features:

- Operates on a designated TCP port.
- Serves static content from a predefined directory.
- Handles HTTP GET requests efficiently.
- Returns proper HTTP status codes:
  1) 200 OK for successful requests.
  2) 404 Not Found if a requested file is missing.
  3) 301 Moved Permanently for redirected resources.
- Logs HTTP request and response headers for debugging.
