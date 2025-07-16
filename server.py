import socket
import threading

HOST = '127.0.0.1'
PORT = 5000

clients = []

def broadcast(data, client_socket):
    """Broadcast data to all clients except the sender."""
    for client in clients:
        if client != client_socket:
            try:
                client.send(data.encode())
            except:
                continue

def handle_client(client_socket, addr):
    """Handle the incoming messages from clients."""
    print(f"New connection from {addr}")
    clients.append(client_socket)

    try:
        while True:
            data = client_socket.recv(1024).decode()
            if data:
                print(f"Received data: {data}")
                broadcast(data, client_socket)
            else:
                break
    except Exception as e:
        print(f"Error receiving data: {e}")
    finally:
        clients.remove(client_socket)
        client_socket.close()

def start_server():
    """Start the server and handle incoming clients."""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server started on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
        client_thread.start()

if __name__ == "__main__":
    start_server()
