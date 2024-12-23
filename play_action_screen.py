#play_action_screen.py
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
import socket
import setup_screen
import pygame
import random
import os
from PIL import Image, ImageTk

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
        self.total_tags = {'red': 0, 'blue': 0}
        self.friendly_fire_counts = {'red': 0, 'blue': 0}

        self.play_screen = None  # We'll create this after the countdown
        self.countdown_window = None
        self.music_thread = None
        pygame.mixer.init()

        self.udp_comm.start_listener(self.handle_udp_message)

        # Start the countdown immediately when the screen is initialized
        self.initiate_countdown()
        
    def initiate_countdown(self):
        """Initiate the countdown in a separate window"""
        self.open_countdown_window()  # Open the countdown window
        self.countdown(30)  # Start countdown from 30

    def open_countdown_window(self):
        """Creates a new window for the countdown"""
        self.countdown_window = tk.Toplevel(self.parent)
        self.countdown_window.title("Countdown")
        self.countdown_window.geometry("300x300")  # Set window size
        self.countdown_window.configure(bg='black')  # Set background color

        self.countdown_label = tk.Label(self.countdown_window, text="", bg='black', fg='white', font=("Arial", 48))
        self.countdown_label.pack(expand=True)  # Center label in the window

    def countdown(self, count):
        """Perform the countdown, displaying numbers and images"""
        if count >= 0:
            # Update the label to show current count
            self.countdown_label.config(text=str(count))

            # Load and display the corresponding countdown image
            self.display_countdown_image(count)

            if count == 14:
                self.start_music()

            # Schedule the next countdown step
            self.countdown_window.after(1200, self.countdown, count - 1)
        else:
            # Once countdown finishes, close the countdown window and start the game
            self.countdown_window.destroy()
            self.start_game()

    def display_countdown_image(self, count):
        """Load and display countdown image on the countdown window"""
        # Construct the image path for countdown number
        image_path = os.path.join("Images", f"{count}.tif")
        print(f"Attempting to load image from: {image_path}")  # Debugging log

        if os.path.isfile(image_path):
            try:
                image = Image.open(image_path)
                image = image.resize((200, 200), Image.LANCZOS)  # Resize for better visibility
                self.current_image = ImageTk.PhotoImage(image)  # Create PhotoImage

                # Set the label to show the image
                self.countdown_label.config(image=self.current_image)
                self.countdown_label.image = self.current_image  # Keep a reference to avoid garbage collection
            except Exception as e:
                print(f"Error loading image {image_path}: {e}")
        else:
            print(f"Image not found: {image_path}")

    def start_music(self):
        """Start the background music at 15 seconds left"""
        music_tracks = [
            "Track01.mp3",
            "Track02.mp3",
            "Track03.mp3",
            "Track04.mp3",
            "Track05.mp3",
            "Track06.mp3",
            "Track07.mp3"
        ]

        # Get the directory of the current script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Choose a random track to play
        selected_track = random.choice(music_tracks)
        
        # Build the full path to the selected music track
        track_path = os.path.join(script_dir, selected_track)

        # Start music in a separate thread to avoid blocking the UI
        self.music_thread = threading.Thread(target=self.play_music, args=(track_path,))
        self.music_thread.start()

    def play_music(self, track_path):
        """Play the selected music track"""
        try:
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(0.5)  # Set the volume (adjust as needed)
            pygame.mixer.music.play(loops=-1, start=0.0)  # Loop indefinitely
            print(f"Started playing music: {track_path}")
        except pygame.error as e:
            print(f"Error loading or playing music: {e}")

    def stop_music(self):
        """Stop the music"""
        if pygame.mixer.music.get_busy():  # Check if music is playing
            pygame.mixer.music.stop()
            print("Music stopped.")
        else:
            print("No music was playing.")
    
    def start_game(self):
        """Start the gameplay window after the countdown finishes"""
        self.play_screen = tk.Toplevel(self.parent)
        self.play_screen.title("Play Action Screen")
        self.play_screen.geometry("1000x800")
        self.play_screen.configure(bg="black")
        
    
        
        
        # Create a canvas for background lines
        self.canvas = tk.Canvas(self.play_screen, bg="black", width=1000, height=800, highlightthickness=0)
        self.canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        # Start drawing background lines
        self.draw_background()
        
        # Frame for the gameplay timer with a white background
        self.timer_frame = tk.Frame(self.play_screen, bg="white")
        self.timer_frame.grid(row=0, column=0, padx=10, pady=10)
        # Gameplay timer label (6 minutes countdown)
        self.gameplay_timer_label = tk.Label(self.play_screen, text="Gameplay Timer: 6:00", font=("Helvetica", 14), bg="green")
        self.gameplay_timer_label.grid(row=1, column=0, padx=10, pady=10)

        self.frame_red_team = tk.LabelFrame(self.play_screen, bg="red")
        self.frame_red_team.grid(row=0, column=0, padx=10, pady=10)

        self.frame_blue_team = tk.LabelFrame(self.play_screen, bg="blue")
        self.frame_blue_team.grid(row=0, column=2, padx=10, pady=10)

        self.setup_team_scores(self.frame_red_team, self.red_team, "red")
        self.setup_team_scores(self.frame_blue_team, self.blue_team, "blue")

        self.frame_action = tk.LabelFrame(self.play_screen, text="Game Action", bg="black", fg="white")
        self.frame_action.grid(row=0, column=1, padx=10, pady=10)

        self.game_action_text = scrolledtext.ScrolledText(self.frame_action, wrap=tk.WORD, width=60, height=30, state='disabled')
        self.game_action_text.pack(padx=10, pady=10)
        
        # Statistics frame (placed directly in the grid at row=0, column=3)
        self.stats_frame = tk.Frame(self.play_screen, bg="black", relief=tk.RAISED, bd=2)
        self.stats_frame.grid(row=1, column=2, padx=10, pady=10, sticky="n")

        # Labels for statistics
        self.winning_team_label = tk.Label(self.stats_frame, text="Winning Team: N/A", bg="black", fg="white", font=("Helvetica", 12))
        self.winning_team_label.pack(pady=5)

        self.top_scorer_label = tk.Label(self.stats_frame, text="Top Scorer: N/A", bg="black", fg="white", font=("Helvetica", 12))
        self.top_scorer_label.pack(pady=5)

        self.red_tags_label = tk.Label(self.stats_frame, text="Red Team Total Tags: 0", bg="black", fg="red", font=("Helvetica", 12))
        self.red_tags_label.pack(pady=5)
        
        self.red_friendly_fire_label = tk.Label(self.stats_frame, text="Red Friendly Fire: 0", bg="black", fg="red", font=("Helvetica", 12))
        self.red_friendly_fire_label.pack(pady=5)
        
        self.blue_tags_label = tk.Label(self.stats_frame, text="Blue Team Total Tags: 0", bg="black", fg="blue", font=("Helvetica", 12))
        self.blue_tags_label.pack(pady=5)
        
        self.blue_friendly_fire_label = tk.Label(self.stats_frame, text="Blue Friendly Fire: 0", bg="black", fg="blue", font=("Helvetica", 12))
        self.blue_friendly_fire_label.pack(pady=5)
        
        self.udp_comm.send_broadcast("202")
        # Start the gameplay timer immediately
        self.start_gameplay_timer()

    def update_statistics(self):
        """Update all displayed statistics dynamically."""
        # Calculate the scores for each team
        red_score = sum(player['score'] for player in self.red_team)
        blue_score = sum(player['score'] for player in self.blue_team)

        # Determine the winning team based on score
        if red_score > blue_score:
            winning_team = "Red Team"
        elif blue_score > red_score:
            winning_team = "Blue Team"
        else:
            winning_team = "Tie"

        self.winning_team_label.config(text=f"Winning Team: {winning_team}")

        # Find the top scoring player by combining red and blue teams
        all_players = self.red_team + self.blue_team
        top_scorer = max(all_players, key=lambda p: p['score'], default=None)

        # Get the top scorer's team
        if top_scorer in self.red_team:
            top_scorer_team = "red"
        elif top_scorer in self.blue_team:
            top_scorer_team = "blue"
        else:
            top_scorer_team = "none"

        # Format the top scorer's text (ensure score includes base hit points)
        top_scorer_text = f"{top_scorer['codename']} ({top_scorer['score']})" if top_scorer else "N/A"
        self.top_scorer_label.config(text=f"Top Scorer: {top_scorer_text}")

        # Update the top scorer label color based on their team
        if top_scorer_team == "red":
            self.top_scorer_label.config(fg="red")
        elif top_scorer_team == "blue":
            self.top_scorer_label.config(fg="blue")
        else:
            self.top_scorer_label.config(fg="white")

        # Update tags and friendly fire counts
        self.red_tags_label.config(text=f"Red Team Tags: {self.total_tags['red']}")
        self.blue_tags_label.config(text=f"Blue Team Tags: {self.total_tags['blue']}")
        self.red_friendly_fire_label.config(text=f"Red Friendly Fire: {self.friendly_fire_counts['red']}")
        self.blue_friendly_fire_label.config(text=f"Blue Friendly Fire: {self.friendly_fire_counts['blue']}")
        
    def draw_background(self):
        
        """Clear the canvas and draw new random lines with a 50/50 chance of being red or blue."""
        # Clear all previous drawings
        self.canvas.delete("all")
        """Draw random lines on the canvas with a 50/50 chance of being red or blue"""
        for _ in range(30):
            start_pos = (random.randint(0, 1000), random.randint(0, 800))
            end_pos = (random.randint(0, 1000), random.randint(0, 800))
            line_color = "red" if random.random() < 0.5 else "blue"  # 50/50 chance for red or blue
            self.canvas.create_line(start_pos, end_pos, fill=line_color, width=2)

        # Schedule the next background update
        self.canvas.after(800, self.draw_background)     
                   
    def start_gameplay_timer(self):
        # After the countdown finishes, start the 6-minute gameplay timer
        self.gameplay_time = 360  # Reset timer to 6 minutes
        self.update_gameplay_timer()  # Update the label immediately with the starting time
        print(f"Gameplay timer started with {self.gameplay_time} seconds.")
        self.run_gameplay_timer()  # Start the countdown for gameplay timer

    def run_gameplay_timer(self):
        # Countdown for 6 minutes (360 seconds)
        if self.gameplay_time > 0:
            self.gameplay_time -= 1
            self.update_gameplay_timer()
            # Schedule the next update in 1 second
            self.play_screen.after(1000, self.run_gameplay_timer)
        else:
            # Timer finished - Trigger end of game (this is just a placeholder)
            self.game_over()

    def update_gameplay_timer(self):
        # Update the timer label in the format MM:SS
        minutes = self.gameplay_time // 60
        seconds = self.gameplay_time % 60
        self.gameplay_timer_label.config(text=f"Gameplay Timer: {minutes:02d}:{seconds:02d}")
        print(f"Updated timer: {minutes:02d}:{seconds:02d}")  # Debugging log

    def game_over(self):
        # This function gets called when the gameplay timer reaches zero
        pygame.mixer.music.stop()
        self.udp_comm.send_broadcast("221")
        self.log_event("Game Over! Time's up.")
        print("Game Over! Time's up.")

    def setup_team_scores(self, frame, team, team_color):
        """Sets up team scores and player labels in the UI."""
        # Add a team score label at the top of the frame
        team_score_label = tk.Label(frame, text=f"{team_color.capitalize()} Team Score: 0", bg=frame.cget("bg"), fg="white", font=("Helvetica", 12))
        team_score_label.pack(anchor='n')  # Pack at the top of the frame
        frame.team_score_label = team_score_label  # Attach to the frame for later updates

        # Add labels for individual players
        for player in team:
            label = tk.Label(frame, text=f"{player['codename']} {player['score']}", bg=frame.cget("bg"), fg="white")
            label.pack(anchor='w')
            player['label'] = label
            player['base_hit'] = False  # Flag to track if player has hit the base

    def handle_udp_message(self, message, addr):
        self.process_hit_message(message)

    def process_score_message(self, message):
        try:
            parts = message.split(":")
            if len(parts) >= 2:
                action = parts[1].strip()
                codename = action.split()[0]  
                self.update_score(codename, increment=1)
                self.log_event(f"{codename} scored a point!")
        except Exception as e:
            self.log_event(f"Error parsing score message: {message}")

    def handle_base_score(self, transmitting_id, team_color):
        # Handle the base score when a player hits a base
        
        if transmitting_id:
            transmitting_player = self.get_player_by_equipment(transmitting_id)
            if transmitting_player:
                # Award points to the player who hit the base
                self.update_score(transmitting_player, increment=100)

                # Add the [B] marker to the player's label to show they hit the base
                self.add_base_marker(transmitting_player)

                # Log the event
                if team_color == "blue":
                    self.log_event(f"{transmitting_player['codename']} Captured the Red Base")
                elif team_color == "red":
                    self.log_event(f"{transmitting_player['codename']} Captured the Blue Base")
            else:
                self.log_event(f"Player with equipment ID {transmitting_id} not found.")
        else:
            self.log_event("No transmitting ID found for base capture.")

    def add_base_marker(self, player):
        # Mark the player as having hit the base
        player['base_hit'] = True
        # Update the label with the [B] next to their codename
        self.update_player_label(player)

    def process_hit_message(self, message):
        try:
            if ':' in message:
                transmitting_id, target = message.split(':')
                transmitting_id = int(transmitting_id)
                hit_id = int(target)

                 # Check if target is a base hit (43 or 53)
                if target == "43":
                    self.handle_base_score(transmitting_id, "red")
                elif target == "53":
                    self.handle_base_score(transmitting_id, "blue")
                else:
                    transmitting_player = self.get_player_by_equipment(transmitting_id)
                    hit_player = self.get_player_by_equipment(hit_id)
                    if transmitting_player and hit_player:
                        same_team = transmitting_player in self.red_team and hit_player in self.red_team or \
                                    transmitting_player in self.blue_team and hit_player in self.blue_team
                        if same_team:
                            # Friendly fire logic
                            self.update_score(transmitting_player, increment=-10)
                            team_color = "red" if transmitting_player in self.red_team else "blue"
                            self.friendly_fire_counts[team_color] += 1

                            # Broadcast the ID of the player getting disabled
                            self.udp_comm.send_broadcast(str(transmitting_id))

                            self.log_event(f"{transmitting_player['codename']} tagged teammate {hit_player['codename']}. Penalty applied!")
                        else:
                            # Normal hit logic
                            self.update_score(transmitting_player, increment=10)
                            team_color = "red" if transmitting_player in self.red_team else "blue"
                            self.total_tags[team_color] += 1

                            self.udp_comm.send_broadcast(str(hit_id))
                            self.log_event(f"{hit_player['codename']} was hit by {transmitting_player['codename']}.")

                        # Update statistics after each hit
            self.update_statistics()
        except ValueError:
            self.log_event(f"Error parsing hit message: {message}")

    def get_player_by_equipment(self, equipment_id):
        for team in [self.red_team, self.blue_team]:
            for player in team:
                if player['equipment_id'] == equipment_id:
                    return player
        return None

    def update_player_label(self, player):
            # Format: [B] Codename Score if they hit the base, else just Codename Score
            if player['base_hit']:
                player['label'].config(text=f"[𝑩] {player['codename']} {player['score']}")
            else:
                player['label'].config(text=f"{player['codename']} {player['score']}")
     
    def update_score(self, player, increment):
        """Update the score of a player and dynamically reorder the team based on scores."""
        # Update player's score
        player['score'] += increment

        # Update player's label text
        player['label'].config(text=f"{player['codename']} {player['score']}")

        # Identify the player's team
        team = self.red_team if player in self.red_team else self.blue_team
        team_color = "Red" if team == self.red_team else "Blue"
        team_frame = self.frame_red_team if team == self.red_team else self.frame_blue_team

        #   Calculate and update the team's total score
        total_team_score = sum(p['score'] for p in team)
        team_frame.team_score_label.config(text=f"{team_color} Team Score: {total_team_score}")

        # Sort players by their scores in descending order
        team.sort(key=lambda p: p['score'], reverse=True)

        #    Remove and re-pack player labels based on the new order
        for widget in team_frame.winfo_children():
            if widget != team_frame.team_score_label:
                widget.pack_forget()  # Remove all labels except the team score label

        for sorted_player in team:
            sorted_player['label'].pack(anchor='w')  # Re-pack labels in sorted order

        print(f"Updated {player['codename']}'s score to {player['score']} and reordered {team_color} Team.")

    def log_event(self, event):
        self.game_action_text.config(state='normal')
        self.game_action_text.insert(tk.END, event + "\n")
        self.game_action_text.see(tk.END)
        self.game_action_text.config(state='disabled')

    def on_close(self):
        self.stop_music()
        self.play_screen.destroy()
        # Optionally, stop the UDP listener thread
        if self.udp_comm.listener_thread is not None:
            self.udp_comm.listener_thread.join()