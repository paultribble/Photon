import socket

def setup_udp_server(host='127.0.0.1', port=1337):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind((host, port))
        print(f"Server listening on {host}:{port}")
        return server_socket 
    except Exception as e:
        print(f"An error occurred while setting up the server: {e}")
        return None

def receive_data(server_socket):
    try:
        while True:
            data, addr = server_socket.recvfrom(1024)
            print(f"Received message from {addr}: {data.decode()}")
            # Process data (add player info and ID)
    except Exception as e:
        print(f"An error occurred while receiving data: {e}")
    finally:
        server_socket.close()

if __name__ == "__main__":
    server_socket = setup_udp_server() 
    if server_socket:  
        receive_data(server_socket)