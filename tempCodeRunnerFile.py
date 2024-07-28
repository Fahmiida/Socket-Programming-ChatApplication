import socket
import os
import threading
import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox

# Constants
BUFFER_SIZE = 1024

# Function to handle uploading a file
def upload_file():
    if not connected:
        messagebox.showerror("Error", "Not connected to the server.")
        return
    filepath = filedialog.askopenfilename()
    if filepath:
        filename = os.path.basename(filepath)
        client_socket.send(f"UPLOAD {filename}".encode())
        with open(filepath, 'rb') as f:
            while True:
                data = f.read(BUFFER_SIZE)
                if not data:
                    break
                client_socket.send(data)
        client_socket.send(b'EOF')
        response = client_socket.recv(BUFFER_SIZE).decode()
        add_message(response)

# Function to handle downloading a file
def download_file():
    if not connected:
        messagebox.showerror("Error", "Not connected to the server.")
        return
    filename = file_entry.get()
    if filename:
        client_socket.send(f"DOWNLOAD {filename}".encode())
        filepath = os.path.join('client_files', filename)
        with open(filepath, 'wb') as f:
            while True:
                data = client_socket.recv(BUFFER_SIZE)
                if data.endswith(b'EOF'):
                    f.write(data[:-3])
                    break
                f.write(data)
        add_message(f"{filename} downloaded successfully.")

# Function to add message to the message box
def add_message(message):
    message_box.config(state=tk.NORMAL)
    message_box.insert(tk.END, message + '\n')
    message_box.config(state=tk.DISABLED)

# Function to handle receiving messages
def receive_messages():
    global connected
    while connected:
        try:
            message = client_socket.recv(BUFFER_SIZE).decode()
            if message:
                add_message(message)
        except:
            break

# Function to send a message
def send_message():
    message = message_entry.get()
    if message:
        client_socket.send(message.encode())
        message_entry.delete(0, tk.END)

# Function to connect to the server
def connect_to_server():
    global client_socket, connected, receive_thread
    if connected:
        messagebox.showinfo("Info", "Already connected to the server.")
        return

    ip_address = ip_entry.get()
    port_number = port_entry.get()
    username = username_entry.get()

    if not ip_address or not port_number or not username:
        messagebox.showerror("Error", "Please enter IP address, port number, and username.")
        return

    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect((ip_address, int(port_number)))
        client_socket.send(username.encode())
        add_message(f"[*] Connected to server as {username}")
        connected = True

        # Start a thread to receive messages
        receive_thread = threading.Thread(target=receive_messages)
        receive_thread.start()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to connect to the server: {e}")

# Function to disconnect from the server
def disconnect_from_server():
    global client_socket, connected
    if not connected:
        messagebox.showinfo("Info", "Not connected to the server.")
        return
    client_socket.send(b'EXIT')
    client_socket.close()
    add_message("[*] Disconnected from server")
    connected = False

if not os.path.exists('client_files'):
    os.makedirs('client_files')

# Initialize global variables
client_socket = None
connected = False
receive_thread = None

# GUI setup
window = tk.Tk()
window.title("Client")

# Username entry
username_frame = tk.Frame(window)
username_frame.pack(pady=5)
tk.Label(username_frame, text="Username:").pack(side=tk.LEFT)
username_entry = tk.Entry(username_frame)
username_entry.pack(side=tk.LEFT)

# IP address and port number entry
ip_frame = tk.Frame(window)
ip_frame.pack(pady=5)
tk.Label(ip_frame, text="IP Address:").pack(side=tk.LEFT)
ip_entry = tk.Entry(ip_frame)
ip_entry.pack(side=tk.LEFT)

port_frame = tk.Frame(window)
port_frame.pack(pady=5)
tk.Label(port_frame, text="Port:").pack(side=tk.LEFT)
port_entry = tk.Entry(port_frame)
port_entry.pack(side=tk.LEFT)

# Connect button
connect_button = tk.Button(window, text="Connect", command=connect_to_server)
connect_button.pack(pady=5)

# Logout button
logout_button = tk.Button(window, text="Logout", command=disconnect_from_server)
logout_button.pack(pady=5)

# File download entry
file_frame = tk.Frame(window)
file_frame.pack(pady=5)
tk.Label(file_frame, text="Filename:").pack(side=tk.LEFT)
file_entry = tk.Entry(file_frame)
file_entry.pack(side=tk.LEFT)

# Upload and Download buttons
upload_button = tk.Button(window, text="Upload File", command=upload_file)
upload_button.pack(pady=5)
download_button = tk.Button(window, text="Download File", command=download_file)
download_button.pack(pady=5)

# Message box
message_frame = tk.Frame(window)
message_frame.pack(pady=10)
message_box = scrolledtext.ScrolledText(message_frame, state=tk.DISABLED, wrap=tk.WORD)
message_box.pack()

# Message entry and send button
send_frame = tk.Frame(window)
send_frame.pack(pady=5)
message_entry = tk.Entry(send_frame, width=50)
message_entry.pack(side=tk.LEFT, padx=5)
send_button = tk.Button(send_frame, text="Send", command=send_message)
send_button.pack(side=tk.LEFT)

window.mainloop()