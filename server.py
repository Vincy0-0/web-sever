import socket
import threading
import os
import time
import mimetypes
from email.utils import formatdate, parsedate_to_datetime
from urllib.parse import unquote

# Server Configuration
HOST = '127.0.0.1'  
PORT = 8080         
LOG_FILE = "server.log"

# Thread lock for thread-safe logging
log_lock = threading.Lock()

def log_request(client_ip, file_name, response_status):
    """
    Records the client request statistics into a log file.
    Format: client IP, access time, requested file name, response type[cite: 26, 27].
    """
    access_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    log_entry = f"IP: {client_ip} | Time: [{access_time}] | File: {file_name} | Status: {response_status}\n"
    
    with log_lock:
        with open(LOG_FILE, "a") as log:
            log.write(log_entry)

def format_http_date(timestamp):
    """Formats an OS timestamp into an RFC 2822 HTTP date string."""
    return formatdate(timeval=timestamp, localtime=False, usegmt=True)

def send_response(conn, status_code, status_msg, headers, filepath=None):
    """Helper function to send HTTP response headers and optional file payload."""
    response_line = f"HTTP/1.1 {status_code} {status_msg}\r\n"
    full_headers = response_line + headers + "\r\n"
    
    # Send headers over TCP connection [cite: 18]
    conn.sendall(full_headers.encode('utf-8'))
    
    # If a filepath is provided (for GET requests), send the file data
    if filepath:
        with open(filepath, 'rb') as f: # 'rb' ensures both text and images are handled properly [cite: 56]
            while chunk := f.read(4096):
                conn.sendall(chunk)

def handle_client(conn, addr):
    """
    Worker function for a single thread. Handles the HTTP request/response exchange[cite: 54, 55].
    """
    conn.settimeout(15.0)  # Timeout for persistent connections
    client_ip = addr[0]

    while True:
        try:
            # Receive the HTTP request [cite: 12]
            request_data = conn.recv(4096).decode('utf-8')
            if not request_data:
                break  # Client closed connection

            lines = request_data.split('\r\n')
            request_line = lines[0]
            
            # Parse Headers
            headers = {}
            for line in lines[1:]:
                if line == '':
                    break
                parts = line.split(': ', 1)
                if len(parts) == 2:
                    headers[parts[0]] = parts[1]

            # Parse Request Line [cite: 9]
            parts = request_line.split()
            if len(parts) != 3:
                send_response(conn, 400, "Bad Request", "Connection: close\r\n")
                log_request(client_ip, "Malformed Request", 400)
                break

            method, path, version = parts
            path = unquote(path)

            # Handle Connection Header [cite: 59, 60]
            conn_header = headers.get("Connection", "close").lower()
            keep_alive = (conn_header == "keep-alive")
            conn_res_header = "Connection: keep-alive\r\n" if keep_alive else "Connection: close\r\n"

            # Check supported methods (GET and HEAD only) [cite: 56]
            if method not in ["GET", "HEAD"]:
                send_response(conn, 400, "Bad Request", conn_res_header)
                log_request(client_ip, path, 400)
                if not keep_alive: break
                continue

            # Default to index.html if root is requested
            if path == '/':
                path = '/index.html'
            
            # Security Check: Prevent directory traversal -> 403 Forbidden [cite: 57]
            if ".." in path:
                send_response(conn, 403, "Forbidden", conn_res_header)
                log_request(client_ip, path, 403)
                if not keep_alive: break
                continue

            filepath = '.' + path

            # Check if file exists -> 404 Not Found [cite: 19, 57]
            if not os.path.exists(filepath) or not os.path.isfile(filepath):
                send_response(conn, 404, "Not Found", conn_res_header)
                log_request(client_ip, path, 404)
                if not keep_alive: break
                continue
            
            # File exists, get Last-Modified time [cite: 10, 58]
            mtime = os.path.getmtime(filepath)
            last_modified_str = format_http_date(mtime)
            last_modified_header = f"Last-Modified: {last_modified_str}\r\n"

            # Handle If-Modified-Since -> 304 Not Modified [cite: 57, 58]
            if_mod_since = headers.get("If-Modified-Since")
            if if_mod_since:
                try:
                    mod_since_dt = parsedate_to_datetime(if_mod_since)
                    file_mtime_dt = parsedate_to_datetime(last_modified_str)
                    
                    if file_mtime_dt <= mod_since_dt:
                        send_response(conn, 304, "Not Modified", conn_res_header + last_modified_header)
                        log_request(client_ip, path, 304)
                        if not keep_alive: break
                        continue
                except (TypeError, ValueError):
                    pass # Ignore malformed date and proceed to send 200 OK

            # Process 200 OK Response [cite: 57]
            mime_type, _ = mimetypes.guess_type(filepath)
            if mime_type is None:
                mime_type = 'application/octet-stream'
            
            content_type_header = f"Content-Type: {mime_type}\r\n"
            content_length = os.path.getsize(filepath)
            content_length_header = f"Content-Length: {content_length}\r\n"

            # Create HTTP response message [cite: 16, 17]
            headers_to_send = conn_res_header + last_modified_header + content_type_header + content_length_header
            
            # Send file only if method is GET [cite: 56]
            send_response(conn, 200, "OK", headers_to_send, filepath if method == "GET" else None)
            log_request(client_ip, path, 200)

            if not keep_alive:
                break

        except socket.timeout:
            break
        except Exception as e:
            print(f"Error handling request: {e}")
            break
    
    conn.close()

def start_server():
    """Initializes the server socket and listens for incoming connections."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((HOST, PORT))
    server_socket.listen(10)
    
    print(f"Server is running on http://{HOST}:{PORT}")
    print("Waiting for client connections...")

    try:
        while True:
            # Create a connection socket when contacted by a client [cite: 11]
            conn, addr = server_socket.accept()
            # Multi-threading: start a new thread for every client connection [cite: 7, 54]
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("\nServer shutting down.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()