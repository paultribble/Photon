#Currently does not work, trying to start basic and scale up once working

import socket

def setup_udp_server(host='127.0.0.1,' , port=1337):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print(f"Server listening on {host}:{port}")
    return server_socket


def receive_data(server_socket):
    while True:
        data, addr = server_socket.recvfrom(1024)
        print(f"Received message from {addr}: {data.decode()}")
        #Process data (add player info and ID)

if __name__ == "__main__":
    setup_udp_server()