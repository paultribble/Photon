# udp_communication.py
import socket
import threading

class UDPCommunication:
    def __init__(self, broadcast_port=7500, receive_port=7501):
        self.broadcast_port = broadcast_port
        self.receive_port = receive_port
        self.sock_broadcast = self.setup_broadcast_socket()
        self.sock_receive = self.setup_receive_socket()
        self.listener_thread = None
        self.receive_callback = None  # Function to call when data is received

    def setup_broadcast_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        return sock

    def setup_receive_socket(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind(('', self.receive_port))
        except OSError as e:
            print(f"Error binding to port {self.receive_port}: {e}")
            sock.close()
            raise e
        return sock

    def start_listener(self, callback):
        self.receive_callback = callback
        self.listener_thread = threading.Thread(target=self.listen_for_data, daemon=True)
        self.listener_thread.start()

    def listen_for_data(self):
        while True:
            try:
                data, addr = self.sock_receive.recvfrom(1024)
                if self.receive_callback:
                    self.receive_callback(data.decode(), addr)
            except Exception as e:
                print(f"Error receiving UDP data: {e}")
                break

    def send_broadcast(self, message):
        try:
            self.sock_broadcast.sendto(message.encode(), ('<broadcast>', self.broadcast_port))
            print(f"Broadcasted message: {message}")
        except Exception as e:
            print(f"Error sending UDP broadcast: {e}")

    def close_sockets(self):
        if self.sock_broadcast:
            self.sock_broadcast.close()
        if self.sock_receive:
            self.sock_receive.close()