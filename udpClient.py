#Currently not working, will scale up once sending and receiving packets works


import socket

def setup_udp_client(host = '127.0.0.1' , port = 1337):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    message = "New player added".encode('utf-8')
    client_socket.sendto(message, ('127.0.0.1' , 1337))
    print("Player added signal sent to server")


    while True:
        data, _ = client_socket.recvfrom(1024)
        print(f"Received from server: {data.decode('utf-8')}")

if __name__ == "__main__":
    setup_udp_client()