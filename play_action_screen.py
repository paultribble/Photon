# play_action_screen.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading

class PlayActionScreen:
    def __init__(self, parent, udp_comm, red_team_players, blue_team_players):
        self.parent = parent
        self.udp_comm = udp_comm
        self.red_team_players = red_team_players
        self.blue_team_players = blue_team_players

        # Initialize player scores
        self.red_team_scores = {codename: 0 for codename in self.red_team_players}
        self.blue_team_scores = {codename: 0 for codename in self.blue_team_players}

        self.play_screen = tk.Toplevel(parent)
        self.play_screen.title("Play Action Screen")
        self.play_screen.geometry("1000x800")

        # Team Score Areas
        self.frame_red_team = tk.LabelFrame(self.play_screen, text="Red Team Scores", bg="red", width=250, height=400)
        self.frame_red_team.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.frame_blue_team = tk.LabelFrame(self.play_screen, text="Blue Team Scores", bg="cyan", width=250, height=400)
        self.frame_blue_team.grid(row=0, column=2, padx=10, pady=10, sticky="n")

        # Initialize team score labels
        self.red_team_labels = {}
        self.blue_team_labels = {}

        self.setup_team_scores(self.frame_red_team, self.red_team_labels, self.red_team_scores)
        self.setup_team_scores(self.frame_blue_team, self.blue_team_labels, self.blue_team_scores)

        # Game Action Area (Scrollable)
        self.frame_action = tk.LabelFrame(self.play_screen, text="Game Action", bg="black", fg="white", width=500, height=600)
        self.frame_action.grid(row=0, column=1, padx=10, pady=10)

        # Scrollable text widget for game action events
        self.game_action_text = scrolledtext.ScrolledText(self.frame_action, wrap=tk.WORD, width=60, height=30, state='disabled')
        self.game_action_text.pack(padx=10, pady=10)

        # Start UDP listener
        self.udp_comm.start_listener(self.handle_udp_message)

        # Handle window close
        self.play_screen.protocol("WM_DELETE_WINDOW", self.on_close)

    def setup_team_scores(self, frame, team_labels_dict, team_scores_dict):
        for codename in team_scores_dict:
            label = tk.Label(frame, text=f"{codename}: {team_scores_dict[codename]}", bg=frame.cget("bg"), fg="white", font=("Arial", 10))
            label.pack(anchor='w', padx=5, pady=2)
            team_labels_dict[codename] = label

    def handle_udp_message(self, message, addr):
        # Parse the message and update scores or log events
        # Example messages:
        # "Tag: PlayerA tagged PlayerB"
        # "Capture: PlayerC captured Base"
        # "Score: PlayerD scored a point"

        if message.startswith("Score:"):
            # Example: "Score: PlayerD scored a point"
            try:
                parts = message.split(":")
                if len(parts) >= 2:
                    action = parts[1].strip()
                    codename = action.split()[0]  # Assuming format "PlayerD scored a point"
                    self.update_score(codename, increment=1)
                    self.log_event(f"{codename} scored a point!")
            except Exception as e:
                self.log_event(f"Error parsing score message: {message}")
        else:
            # Log other game actions
            self.log_event(f"{message} from {addr}")

    def update_score(self, codename, increment=1):
        # Check if codename is in red team
        if codename in self.red_team_scores:
            self.red_team_scores[codename] += increment
            self.red_team_labels[codename].config(text=f"{codename}: {self.red_team_scores[codename]}")
        # Check if codename is in blue team
        elif codename in self.blue_team_scores:
            self.blue_team_scores[codename] += increment
            self.blue_team_labels[codename].config(text=f"{codename}: {self.blue_team_scores[codename]}")
        else:
            self.log_event(f"Unknown player: {codename}")

    def log_event(self, event):
        self.game_action_text.config(state='normal')
        self.game_action_text.insert(tk.END, event + "\n")
        self.game_action_text.see(tk.END)
        self.game_action_text.config(state='disabled')

    def on_close(self):
        self.play_screen.destroy()
