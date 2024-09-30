# play_action_screen.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading

class PlayActionScreen:
    def __init__(self, parent, udp_comm):
        self.parent = parent
        self.udp_comm = udp_comm

        self.play_screen = tk.Toplevel(parent)
        self.play_screen.title("Play Action Screen")
        self.play_screen.geometry("1000x800")

        # Team Score Areas
        self.frame_red_team = tk.LabelFrame(self.play_screen, text="Red Team Scores", bg="red", width=250, height=400)
        self.frame_red_team.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.frame_blue_team = tk.LabelFrame(self.play_screen, text="Blue Team Scores", bg="cyan", width=250, height=400)
        self.frame_blue_team.grid(row=0, column=2, padx=10, pady=10, sticky="n")

        # Initialize team score labels
        self.red_team_scores = {}
        self.blue_team_scores = {}

        self.setup_team_scores(self.frame_red_team, self.red_team_scores)
        self.setup_team_scores(self.frame_blue_team, self.blue_team_scores)

        # Game Action Area (Scrollable)
        self.frame_action = tk.LabelFrame(self.play_screen, text="Game Action", bg="black", fg="white", width=500, height=600)
        self.frame_action.grid(row=0, column=1, padx=10, pady=10)

        # Scrollable text widget for game action events
        self.game_action_text = scrolledtext.ScrolledText(self.frame_action, wrap=tk.WORD, width=60, height=30, state='disabled')
        self.game_action_text.pack(padx=10, pady=10)

        # Bind UDP receive callback to update game action area
        self.udp_comm.start_listener(self.handle_udp_message)

    def setup_team_scores(self, frame, team_scores_dict):
        # For simplicity, initialize all scores to 0
        for i in range(15):
            label = tk.Label(frame, text=f"Player {i+1}: 0", bg=frame.cget("bg"), fg="white", font=("Arial", 10))
            label.pack(anchor='w', padx=5, pady=2)
            team_scores_dict[f"Player {i+1}"] = label

    def handle_udp_message(self, message, addr):
        # Here you can parse the message and update scores or log events
        # For simplicity, we'll log all messages to the game action area
        game_event = f"{message} from {addr}"
        print(game_event)  # Print to console

        # Update the game action text area
        self.game_action_text.config(state='normal')  # Make text widget editable
        self.game_action_text.insert(tk.END, game_event + "\n")  # Add new event
        self.game_action_text.see(tk.END)  # Auto-scroll to the latest entry
        self.game_action_text.config(state='disabled')  # Make it read-only again

    def log_event(self, event):
        self.game_action_text.config(state='normal')
        self.game_action_text.insert(tk.END, event + "\n")
        self.game_action_text.see(tk.END)
        self.game_action_text.config(state='disabled')

    def close_screen(self):
        self.play_screen.destroy()
