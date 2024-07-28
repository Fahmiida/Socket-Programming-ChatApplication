import socket
import threading
import os
import tkinter as tk
from tkinter import scrolledtext

# Constants
HOST = '127.0.0.1'
PORT = 12345
BUFFER_SIZE = 1024
SERVER_DIR = 'server_files'

# Create server directory if it does not exist
if not os.path.exists(SERVER_DIR):
    os.makedirs(SERVER_DIR)

clients = {}
client_addresses = {}
client_usernames = {}

# Function to handle client connections
def handle_client(client_socket, client_address):
    client_id = client_address[1]
    try:
        username = client_socket.recv(BUFFER_SIZE).decode()
    except Exception as e:
        add_message(f"[-] Error receiving username: {e}")
        client_socket.close()
        return
    
    clients[client_id] = client_socket
    client_addresses[client_id] = client_address
    client_usernames[client_id] = username
    update_client_list()
    
    add_message(f"[+] New connection from {client_address} as {username}")
    
    while True:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode()
            if not message:
                break
            
            if message.startswith('UPLOAD'):
                _, filename = message.split()
                filepath = os.path.join(SERVER_DIR, filename)
                with open(filepath, 'wb') as f:
                    while True:
                        data = client_socket.recv(BUFFER_SIZE)
                        if data.endswith(b'EOF'):
                            f.write(data[:-3])
                            break
                        f.write(data)
                client_socket.send(f"{filename} uploaded successfully.".encode())
                add_message(f"{filename} uploaded by {username} ({client_address})")
            
            elif message.startswith('DOWNLOAD'):
                _, filename = message.split()
                filepath = os.path.join(SERVER_DIR, filename)
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        while True:
                            data = f.read(BUFFER_SIZE)
                            if not data:
                                break
                            client_socket.send(data)
                    client_socket.send(b'EOF')
                else:
                    client_socket.send(f"{filename} not found.".encode())
                add_message(f"{filename} downloaded by {username} ({client_address})")
            
            elif message == 'EXIT':
                break
            
            else:
                broadcast_message(f"{username}: {message}")
                add_message(f"{username} ({client_address}): {message}")
                
        except Exception as e:
            add_message(f"[-] Error: {e}")
            break
    
    client_socket.close()
    del clients[client_id]
    del client_addresses[client_id]
    del client_usernames[client_id]
    update_client_list()
    add_message(f"[-] Connection from {client_address} ({username}) closed")

# Function to broadcast messages to all clients
def broadcast_message(message):
    for client_socket in clients.values():
        client_socket.send(message.encode())

# Function to start the server
def start_server():
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    add_message("[*] Server started")
    
    try:
        while True:
            client_socket, client_address = server_socket.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()
    except KeyboardInterrupt:
        stop_server()

# Function to stop the server
def stop_server():
    for client in clients.values():
        client.close()
    server_socket.close()
    add_message("[*] Server stopped")
    window.quit()

# Function to add message to the GUI
def add_message(message):
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, message + '\n')
    message_box.config(state=tk.DISABLED)

# Function to update the client list in the GUI
def update_client_list():
    client_list_box.config(state=tk.NORMAL)
    client_list_box.delete(1.0, tk.END)
    for client_id, client_address in client_addresses.items():
        username = client_usernames.get(client_id, "Unknown")
        client_list_box.insert(tk.END, f"{username} ({client_address})\n")
    client_list_box.config(state=tk.DISABLED)

# GUI setup
window = tk.Tk()
window.title("Server")

# Message box
message_frame = tk.Frame(window)
message_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
message_box = scrolledtext.ScrolledText(message_frame, state=tk.DISABLED, wrap=tk.WORD)
message_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Client list box
client_list_frame = tk.Frame(window)
client_list_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
client_list_box = scrolledtext.ScrolledText(client_list_frame, state=tk.DISABLED, wrap=tk.WORD)
client_list_box.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# Start and stop buttons
button_frame = tk.Frame(window)
button_frame.pack(side=tk.BOTTOM)
start_button = tk.Button(button_frame, text="Start Server", command=lambda: threading.Thread(target=start_server).start())
start_button.pack(side=tk.LEFT)
stop_button = tk.Button(button_frame, text="Stop Server", command=stop_server)
stop_button.pack(side=tk.RIGHT)

window.mainloop()

