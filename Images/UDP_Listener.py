# udp_listener.py
import socket

def udp_listener():
    # Set up a UDP socket to listen for incoming data
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Bind the socket to all available interfaces and port 7500
    try:
        sock.bind(('', 7500))
    except OSError as e:
        print(f"Error binding to port 7500: {e}")
        return

    print("Listening for incoming UDP data on port 7500...")

    try:
        while True:
            data, addr = sock.recvfrom(1024)  # Receive up to 1024 bytes
            print(f"Received message: {data.decode()} from {addr}")
    except KeyboardInterrupt:
        print("\nShutting down listener.")
    finally:
        sock.close()
        print("Socket closed.")

if __name__ == "__main__":
    udp_listener()

