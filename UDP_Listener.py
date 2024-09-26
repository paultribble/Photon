import socket

def udp_listener():
    # Set up a UDP socket to listen for incoming data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    # Bind the socket to all available interfaces ('') and the desired port (7500 in your case)
    sock.bind(('', 7500))

    print("Listening for incoming UDP data on port 7500...")

    while True:
        # Receive up to 1024 bytes of data
        data, addr = sock.recvfrom(1024)
        print(f"Received message: {data.decode()} from {addr}")

if __name__ == "__main__":
    udp_listener()
