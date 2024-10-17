import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import socket
import setup_screen

class UDPCommunication:
    def __init__(self, broadcast_port, client_port):
        self.broadcast_port = broadcast_port
        self.client_port = client_port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('', self.client_port))
        self.listener_thread = None

    def broadcast_message(self, message):
        self.server_socket.sendto(str.encode(message), ('<broadcast>', self.broadcast_port))

    def start_listener(self, message_handler):
        self.listener_thread = threading.Thread(target=self.listen_for_messages, args=(message_handler,))
        self.listener_thread.start()

    def listen_for_messages(self, message_handler):
        while True:
            data, addr = self.server_socket.recvfrom(1024)
            message = data.decode('utf-8')
            message_handler(message, addr)

class PlayActionScreen:
    def __init__(self, parent, udp_comm, red_team, blue_team):
        self.parent = parent
        self.udp_comm = udp_comm
        self.red_team = red_team
        self.blue_team = blue_team

        self.play_screen = tk.Toplevel(parent)
        self.play_screen.title("Play Action Screen")
        self.play_screen.geometry("1000x800")

        self.frame_red_team = tk.LabelFrame(self.play_screen, text="Red Team", bg="red")
        self.frame_red_team.grid(row=0, column=0, padx=10, pady=10)

        self.frame_blue_team = tk.LabelFrame(self.play_screen, text="Blue Team", bg="cyan")
        self.frame_blue_team.grid(row=0, column=2, padx=10, pady=10)

        self.setup_team_scores(self.frame_red_team, self.red_team)
        self.setup_team_scores(self.frame_blue_team, self.blue_team)

        self.frame_action = tk.LabelFrame(self.play_screen, text="Game Action", bg="black", fg="white")
        self.frame_action.grid(row=0, column=1, padx=10, pady=10)

        self.game_action_text = scrolledtext.ScrolledText(self.frame_action, wrap=tk.WORD, width=60, height=30, state='disabled')
        self.game_action_text.pack(padx=10, pady=10)

        self.udp_comm.start_listener(self.handle_udp_message)

    def setup_team_scores(self, frame, team):
        for player in team:
            label = tk.Label(frame, text=f"{player['codename']}: {player['score']}", bg=frame.cget("bg"), fg="white")
            label.pack(anchor='w')
            player['label'] = label

    def handle_udp_message(self, message, addr):
        # Handle the received UDP message
        if message.startswith("Score:"):
            # Example: "Score: PlayerD scored a point"
            self.process_score_message(message)
        elif message == "53":
            self.handle_base_score("green")
        elif message == "43":
            self.handle_base_score("red")
        else:
            self.process_hit_message(message)

    def process_score_message(self, message):
        try:
            parts = message.split(":")
            if len(parts) >= 2:
                action = parts[1].strip()
                codename = action.split()[0]  # Assuming format "PlayerD scored a point"
                self.update_score(codename, increment=1)
                self.log_event(f"{codename} scored a point!")
        except Exception as e:
            self.log_event(f"Error parsing score message: {message}")

    def handle_base_score(self, team_color):
        if team_color == "green":
            for codename in self.blue_team_scores:
                self.update_score(codename, increment=100)
                self.log_event(f"{codename} scored 100 points! [Green Base Captured]")
        elif team_color == "red":
            for codename in self.red_team_scores:
                self.update_score(codename, increment=100)
                self.log_event(f"{codename} scored 100 points! [Red Base Captured]")

    def process_hit_message(self, message):
        # Example message format: "equipment_id:equipment_id"
        try:
            transmitting_id, hit_id = map(int, message.split(':'))
            transmitting_codename = self.get_codename_by_equipment_id(transmitting_id)
            hit_codename = self.get_codename_by_equipment_id(hit_id)
            if transmitting_codename and hit_codename:
                self.log_event(f"{hit_codename} was hit by {transmitting_codename}.")
                # Optionally, send back the equipment ID of the player that got hit
                self.udp_comm.broadcast_message(str(hit_id))
        except ValueError:
            self.log_event(f"Invalid message format received: {message}")

    def get_player_by_equipment(self, equipment_id):
        for team in [self.red_team, self.blue_team]:
            for player in team:
                if player['equipment_id'] == equipment_id:
                    return player
        return None

    def update_score(self, player, increment):
        player['score'] += increment
        player['label'].config(text=f"{player['codename']}: {player['score']}")

    def log_event(self, event):
        self.game_action_text.config(state='normal')
        self.game_action_text.insert(tk.END, event + "\n")
        self.game_action_text.see(tk.END)
        self.game_action_text.config(state='disabled')

    def on_close(self):
        self.play_screen.destroy()
        # Optionally, stop the UDP listener thread
        if self.udp_comm.listener_thread is not None:
            self.udp_comm.listener_thread.join()