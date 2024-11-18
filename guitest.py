import socket
import threading
import random
import psycopg2
import sys
import tkinter as tk
from tkinter import ttk, scrolledtext
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from setup_screen import play_music
import atexit
import time
import pygame

# Global variables for sockets to allow cleanup
sock_broadcast = None
sock_receive = None

# Database connection
def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname="photon",
            user="student",
            # password="student",
            # host="localhost",
            # port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        sys.exit(1)

# Set up UDP broadcast socket
def setup_udp_broadcast_socket():
    global sock_broadcast
    sock_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return sock_broadcast

# Set up UDP receive socket with SO_REUSEADDR
def setup_udp_receive_socket():
    global sock_receive
    sock_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_receive.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock_receive.bind(('', 7501))
    except OSError as e:
        print(f"Error binding to port 7501: {e}")
        sys.exit(1)
    return sock_receive

# Clean up sockets on exit
def cleanup():
    global sock_broadcast, sock_receive
    if sock_broadcast:
        sock_broadcast.close()
    if sock_receive:
        sock_receive.close()
    print("Sockets closed.")

atexit.register(cleanup)

# Splash Screen Function
def show_splash_screen():
    splash = tk.Toplevel()
    splash.title("Welcome to Photon Laser Tag!")
    splash.geometry("400x300")
    splash.configure(bg='black')

    # Load the image
    try:
        logo_path = "Images/logo.jpg"  # Path to your image
        logo_image = Image.open(logo_path)  # Open the image
        logo_image = logo_image.resize((300, 200), Image.LANCZOS)  # Resize the image (optional)
        logo_photo = ImageTk.PhotoImage(logo_image)  # Create a PhotoImage object

        label = tk.Label(splash, image=logo_photo, bg='black')
        label.image = logo_photo  # Keep a reference to the image
        label.pack(expand=True)
    except Exception as e:
        label = tk.Label(splash, text="Photon Laser Tag", bg='black', fg='white', font=("Arial", 20))
        label.pack(expand=True)

    # Close splash screen after 3 seconds
    splash.after(3000, splash.destroy)  # 3000 milliseconds = 3 seconds

# Function to start the main window after splash
def start_main_window():
    root.deiconify()  # Show the main window after the splash screen

# Function to update codename field dynamically based on typed ID
def update_codename(player_id_var, codename_entry, conn):
    player_id = player_id_var.get()

    # Clear the codename entry field before updating
    codename_entry.config(state='normal')
    codename_entry.delete(0, tk.END)

    if player_id.isdigit():  # Check if the input is numeric
        cursor = conn.cursor()
        cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
        result = cursor.fetchone()

        if result:
            codename_entry.insert(0, result[0])  # Insert codename
            codename_entry.config(fg='gray')    # Set text color to gray
        else:
            codename_entry.insert(0, "Invalid ID")
            codename_entry.config(fg='gray')  # Set text color to gray
    else:
        codename_entry.config(fg='black')  # Reset color to black for non-numeric input

    codename_entry.config(state='readonly')

# Modified validate_and_broadcast to reset the color once Enter is pressed
def validate_and_broadcast(player_id_var, codename_entry, equipment_entry, conn, sock_broadcast, play_action_screen=None):
    cursor = conn.cursor()
    player_id = player_id_var.get()
    equipment_id = equipment_entry.get()

    if player_id:  # If ID is not empty
        cursor.execute("SELECT codename, team FROM players WHERE id = %s", (player_id,))
        result = cursor.fetchone()
        if result:
            codename_entry.config(state='normal')
            codename_entry.delete(0, tk.END)
            codename_entry.insert(0, result[0])  # Insert fetched codename
            codename_entry.config(fg='black')    # Reset color to black once validated
            codename_entry.config(state='readonly')
        else:
            codename_entry.config(state='normal')
            codename_entry.delete(0, tk.END)
            codename_entry.insert(0, "Invalid ID")
            codename_entry.config(fg='gray')  # Keep text gray if ID is invalid
            codename_entry.config(state='readonly')
            return

    if equipment_id:
        message = f"Equipment ID: {equipment_id}"  # Send only the Equipment ID
        sock_broadcast.sendto(message.encode(), ('<broadcast>', 7500))  # Broadcast on port 7500
        print(f"Sent: {message}")  # Log the sent message

        # If Play Action Screen is open, log the event
        if play_action_screen and play_action_screen.is_open:
            play_action_screen.log_event(f"Player ID {player_id} equipped with Equipment ID {equipment_id}")
    else:
        messagebox.showwarning("Warning", "Equipment ID cannot be empty.")

# In create_input_form, bind the update_codename function to the player ID entry
def create_input_form(frame, team_name, color, row, col, conn, sock_broadcast, play_action_screen=None):
    team_label = tk.Label(frame, text=team_name, bg=color, font=("Arial", 12, "bold"), width=10)
    team_label.grid(row=0, column=col, padx=10)

    tk.Label(frame, text="ID", font=("Arial", 10, "bold"), width=8).grid(row=1, column=col, padx=5)
    tk.Label(frame, text="Codename", font=("Arial", 10, "bold"), width=10).grid(row=1, column=col + 1, padx=5)
    tk.Label(frame, text="Equipment", font=("Arial", 10, "bold"), width=10).grid(row=1, column=col + 2, padx=5)

    entries = []
    for i in range(15):
        player_id_var = tk.StringVar()
        entry_id = tk.Entry(frame, width=8, textvariable=player_id_var)
        entry_codename = tk.Entry(frame, width=15, state='readonly')
        equipment_combobox = ttk.Combobox(frame, width=5, values=list(range(1, 999)))
        equipment_combobox.set("")  # Set default value

        entry_id.grid(row=i + 2, column=col, padx=5, pady=2)
        entry_codename.grid(row=i + 2, column=col + 1, padx=5, pady=2)
        equipment_combobox.grid(row=i + 2, column=col + 2, padx=5, pady=2)

        # Bind the update_codename function to player ID field updates
        player_id_var.trace_add('write', lambda name, index, mode, pid_var=player_id_var, codename=entry_codename: update_codename(pid_var, codename, conn))

        # Add enter button to validate and broadcast
        enter_button = tk.Button(
            frame,
            text="Enter",
            command=lambda pid_var=player_id_var, codename=entry_codename, equip=equipment_combobox: validate_and_broadcast(
                pid_var, codename, equip, conn, sock_broadcast, play_action_screen),
            width=10
        )
        enter_button.grid(row=i + 2, column=col + 3, padx=5, pady=2)

        entries.append((entry_id, entry_codename, equipment_combobox))

    return entries

# Function to listen for incoming UDP data and update the game action area
def listen_for_data(sock_receive, play_action_screen):
    while True:
        try:
            data, addr = sock_receive.recvfrom(1024)  # Receive up to 1024 bytes
            game_event = f"{data.decode()} from {addr}"
            print(game_event)  # Print to console

            # Handle specific codes
            if game_event.strip() == "202":
                # Game start signal
                if play_action_screen and play_action_screen.is_open:
                    play_action_screen.log_event("Game Started!")
            elif game_event.strip() == "221":
                # Game end signal
                if play_action_screen and play_action_screen.is_open:
                    play_action_screen.log_event("Game Ended!")
            elif ':' in game_event:
                # Handle equipment ID messages or tagging
                parts = game_event.split(':')
                if len(parts) == 2:
                    sender_eq_id = parts[0].split()[-1]  # Extract Equipment ID
                    receiver_eq_id = parts[1].strip()

                    # Map Equipment IDs to player info
                    sender_info = get_player_info_by_eq_id(sender_eq_id)
                    receiver_info = get_player_info_by_eq_id(receiver_eq_id)

                    if receiver_info:
                        if receiver_eq_id.isdigit():
                            # Sender tagged receiver
                            if sender_info['team'] == receiver_info['team']:
                                # Self-tagging
                                transmit_equipment_id(sender_eq_id)
                                if play_action_screen and play_action_screen.is_open:
                                    play_action_screen.log_event(f"Player {sender_info['codename']} tagged themselves.")
                            else:
                                # Valid tag
                                transmit_equipment_id(receiver_eq_id)
                                if play_action_screen and play_action_screen.is_open:
                                    play_action_screen.log_event(f"Player {sender_info['codename']} tagged Player {receiver_info['codename']}.")

                    elif receiver_eq_id == "43":
                        # Green base scored
                        handle_base_scored("green")
                    elif receiver_eq_id == "53":
                        # Red base scored
                        handle_base_scored("red")
            else:
                # Other messages
                if play_action_screen and play_action_screen.is_open:
                    play_action_screen.log_event(game_event)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

# Function to transmit equipment ID
def transmit_equipment_id(equipment_id):
    global sock_broadcast
    message = equipment_id
    sock_broadcast.sendto(message.encode(), ('<broadcast>', 7500))  # Broadcast on port 7500
    print(f"Sent Equipment ID: {message}")

# Function to get player info by equipment ID
def get_player_info_by_eq_id(equipment_id):
    cursor = conn.cursor()
    cursor.execute("SELECT id, codename, team FROM players WHERE equipment_id = %s", (equipment_id,))
    result = cursor.fetchone()
    if result:
        return {'id': result[0], 'codename': result[1], 'team': result[2]}
    return None

# Function to handle base scoring
def handle_base_scored(base_color):
    cursor = conn.cursor()
    if base_color == "red":
        # Green team scores
        cursor.execute("SELECT id, codename FROM players WHERE team = 'green'")
        green_players = cursor.fetchall()
        for player in green_players:
            player_id, codename = player
            # Update score
            cursor.execute("UPDATE players SET score = score + 100 WHERE id = %s", (player_id,))
            # Update codename with 'B' if not already present
            if not codename.startswith("B "):
                new_codename = f"B {codename}"
                cursor.execute("UPDATE players SET codename = %s WHERE id = %s", (new_codename, player_id))
        conn.commit()
        if play_action_screen_instance and play_action_screen_instance.is_open:
            play_action_screen_instance.log_event("Green base scored by Red team!")
    elif base_color == "green":
        # Red team scores
        cursor.execute("SELECT id, codename FROM players WHERE team = 'red'")
        red_players = cursor.fetchall()
        for player in red_players:
            player_id, codename = player
            # Update score
            cursor.execute("UPDATE players SET score = score + 100 WHERE id = %s", (player_id,))
            # Update codename with 'B' if not already present
            if not codename.startswith("B "):
                new_codename = f"B {codename}"
                cursor.execute("UPDATE players SET codename = %s WHERE id = %s", (new_codename, player_id))
        conn.commit()
        if play_action_screen_instance and play_action_screen_instance.is_open:
            play_action_screen_instance.log_event("Red base scored by Green team!")

# Function to clear the database
def clear_database(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players")
    conn.commit()
    print("Database cleared.")
    messagebox.showinfo("Success", "Database has been cleared.")

# View database function
def show_database_menu_tk(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, codename, team FROM players ORDER BY codename ASC")
    entries = cursor.fetchall()

    database_window = tk.Toplevel(root)
    database_window.title("Player Database")

    for i, (player_id, codename, team) in enumerate(entries):
        tk.Label(database_window, text=f"ID: {player_id} | Codename: {codename} | Team: {team}").grid(row=i, column=0, padx=5, pady=2)
        tk.Button(database_window, text="Delete", command=lambda pid=player_id: delete_player(pid, conn)).grid(row=i, column=1, padx=5, pady=2)

# Function to add a new player through a Tkinter dialog
def add_new_player_tk(conn):
    codename = simpledialog.askstring("Input", "Enter New Codename:")
    if codename:
        team = simpledialog.askstring("Input", "Enter Team (red/blue):")
        if team and team.lower() in ['red', 'blue']:
            team = team.lower()
            cursor = conn.cursor()
            while True:
                new_id = random.randint(1, 9999)  # Generate a new ID between 1 and 9999
                cursor.execute("SELECT * FROM players WHERE id = %s", (new_id,))
                if cursor.fetchone() is None:
                    # Assign a unique equipment_id
                    new_eq_id = random.randint(1000, 9999)
                    cursor.execute("SELECT * FROM players WHERE equipment_id = %s", (new_eq_id,))
                    if cursor.fetchone() is None:
                        cursor.execute("INSERT INTO players (id, codename, team, equipment_id, score) VALUES (%s, %s, %s, %s, %s)", 
                                       (new_id, codename, team, new_eq_id, 0))
                        conn.commit()
                        messagebox.showinfo("Success", f"New Player Added: ID={new_id}, Codename={codename}, Team={team}, Equipment ID={new_eq_id}")
                        break
        else:
            messagebox.showwarning("Invalid Team", "Team must be 'red' or 'blue'.")

# Function to delete a player
def delete_player(player_id, conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE id = %s", (player_id,))
    conn.commit()
    messagebox.showinfo("Success", f"Player with ID={player_id} has been deleted.")

# Class for Play Action Screen
class PlayActionScreen:
    def __init__(self, master):
        self.master = master
        self.play_screen = tk.Toplevel(master)
        self.play_screen.title("Play Action Screen")
        self.play_screen.geometry("1000x800")
        self.is_open = True

        # Team Score Areas
        self.frame_red_team = tk.LabelFrame(self.play_screen, text="Red Team Scores", bg="red", fg="white", font=("Arial", 12, "bold"), width=250, height=400)
        self.frame_red_team.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.frame_blue_team = tk.LabelFrame(self.play_screen, text="Blue Team Scores", bg="cyan", fg="white", font=("Arial", 12, "bold"), width=250, height=400)
        self.frame_blue_team.grid(row=0, column=2, padx=10, pady=10, sticky="n")

        # Initialize team score labels
        self.red_team_scores = {}
        self.blue_team_scores = {}

        self.setup_team_scores(self.frame_red_team, self.red_team_scores, "red")
        self.setup_team_scores(self.frame_blue_team, self.blue_team_scores, "blue")

        # Game Action Area (Scrollable)
        self.frame_action = tk.LabelFrame(self.play_screen, text="Game Action", bg="black", fg="white", font=("Arial", 12, "bold"), width=500, height=600)
        self.frame_action.grid(row=0, column=1, padx=10, pady=10)

        # Scrollable text widget for game action events
        self.game_action_text = scrolledtext.ScrolledText(self.frame_action, wrap=tk.WORD, width=60, height=30, state='disabled')
        self.game_action_text.pack(padx=10, pady=10)

        # Handle window close
        self.play_screen.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start periodic score update
        self.update_scores()

    def setup_team_scores(self, frame, team_scores_dict, team_color):
        cursor = conn.cursor()
        cursor.execute("SELECT id, codename, score FROM players WHERE team = %s", (team_color,))
        players = cursor.fetchall()
        for player in players:
            player_id, codename, score = player
            label = tk.Label(frame, text=f"{codename}: {score}", bg=frame.cget("bg"), fg="white", font=("Arial", 10))
            label.pack(anchor='w', padx=5, pady=2)
            team_scores_dict[player_id] = label

    def log_event(self, event):
        self.game_action_text.config(state='normal')
        self.game_action_text.insert(tk.END, event + "\n")
        self.game_action_text.see(tk.END)
        self.game_action_text.config(state='disabled')

    def update_scores(self):
        cursor = conn.cursor()
        # Update Red Team Scores
        cursor.execute("SELECT id, codename, score FROM players WHERE team = 'red'")
        red_players = cursor.fetchall()
        for player in red_players:
            player_id, codename, score = player
            if player_id in self.red_team_scores:
                self.red_team_scores[player_id].config(text=f"{codename}: {score}")
            else:
                label = tk.Label(self.frame_red_team, text=f"{codename}: {score}", bg=self.frame_red_team.cget("bg"), fg="white", font=("Arial", 10))
                label.pack(anchor='w', padx=5, pady=2)
                self.red_team_scores[player_id] = label

        # Update Blue Team Scores
        cursor.execute("SELECT id, codename, score FROM players WHERE team = 'blue'")
        blue_players = cursor.fetchall()
        for player in blue_players:
            player_id, codename, score = player
            if player_id in self.blue_team_scores:
                self.blue_team_scores[player_id].config(text=f"{codename}: {score}")
            else:
                label = tk.Label(self.frame_blue_team, text=f"{codename}: {score}", bg=self.frame_blue_team.cget("bg"), fg="white", font=("Arial", 10))
                label.pack(anchor='w', padx=5, pady=2)
                self.blue_team_scores[player_id] = label

        # Schedule the next update
        self.play_screen.after(1000, self.update_scores)

    def on_close(self):
        self.is_open = False
        self.stop_music()
        self.play_screen.destroy()

# Function to show the Play Action Screen
def show_play_action_screen():
    global play_action_screen_instance
    if play_action_screen_instance is None or not play_action_screen_instance.is_open:
        play_action_screen_instance = PlayActionScreen(root)
        # Start the listener thread with the new play action screen
        listener_thread = threading.Thread(target=listen_for_data, args=(sock_receive, play_action_screen_instance), daemon=True)
        listener_thread.start()
        # Start the game countdown
        start_game_countdown(play_action_screen_instance)
    else:
        play_action_screen_instance.play_screen.lift()

# Function to start game countdown
def start_game_countdown(play_action_screen):
    #pygame.mixer.init()
    #pygame.mixer.music.load("Track07.mp3")
    play_music()
    countdown_window = tk.Toplevel(root)
    countdown_window.title("Game Starting")
    countdown_window.geometry("300x200")
    countdown_window.configure(bg='black')

    label = tk.Label(countdown_window, text="Game Starting in:", bg='black', fg='white', font=("Arial", 16))
    label.pack(pady=20)

    countdown_label = tk.Label(countdown_window, text="5", bg='black', fg='white', font=("Arial", 48))
    countdown_label.pack(pady=20)

    def countdown(n):
        if n >= 0:
            countdown_label.config(text=str(n))
            countdown_window.after(1000, countdown, n-1)
        else:
            countdown_window.destroy()
            # Send code 202 to start the game
            sock_broadcast.sendto('202'.encode(), ('<broadcast>', 7500))
            play_action_screen.log_event("Game Started!")

    # Start playing the music 5 seconds before the countdown starts *****************************************************************
    def start_music():
        pygame.mixer.music.play(-1) # Loop the music
    
    # Schedule the music to start 5 seconds before the countdown
    countdown_window.after(5000, start_music)
    
    countdown(5)

# Function to end the game
def end_game(play_action_screen):
    for _ in range(3):
        sock_broadcast.sendto('221'.encode(), ('<broadcast>', 7500))
        print("Sent: 221")
        play_action_screen.log_event("Game Ended!")
        time.sleep(1)  # Brief pause between sends
    pygame.mixer.music.stop()  # Stop the music

# Function to listen for incoming UDP data and update the game action area
def listen_for_data(sock_receive, play_action_screen):
    while True:
        try:
            data, addr = sock_receive.recvfrom(1024)  # Receive up to 1024 bytes
            game_event = f"{data.decode()} from {addr}"
            print(game_event)  # Print to console

            # Handle specific codes
            if game_event.strip() == "202":
                # Game start signal
                if play_action_screen and play_action_screen.is_open:
                    play_action_screen.log_event("Game Started!")
            elif game_event.strip() == "221":
                # Game end signal
                if play_action_screen and play_action_screen.is_open:
                    play_action_screen.log_event("Game Ended!")
            elif ':' in game_event:
                # Handle equipment ID messages or tagging
                parts = game_event.split(':')
                if len(parts) == 2:
                    sender_eq_id = parts[0].split()[-1]  # Extract Equipment ID
                    receiver_eq_id = parts[1].strip()

                    # Map Equipment IDs to player info
                    sender_info = get_player_info_by_eq_id(sender_eq_id)
                    receiver_info = get_player_info_by_eq_id(receiver_eq_id)

                    if receiver_info:
                        if receiver_eq_id.isdigit():
                            # Sender tagged receiver
                            if sender_info['team'] == receiver_info['team']:
                                # Self-tagging
                                transmit_equipment_id(sender_eq_id)
                                if play_action_screen and play_action_screen.is_open:
                                    play_action_screen.log_event(f"Player {sender_info['codename']} tagged themselves.")
                            else:
                                # Valid tag
                                transmit_equipment_id(receiver_eq_id)
                                if play_action_screen and play_action_screen.is_open:
                                    play_action_screen.log_event(f"Player {sender_info['codename']} tagged Player {receiver_info['codename']}.")
                    elif receiver_eq_id == "43":
                        # Green base scored
                        handle_base_scored("green")
                    elif receiver_eq_id == "53":
                        # Red base scored
                        handle_base_scored("red")
            else:
                # Other messages
                if play_action_screen and play_action_screen.is_open:
                    play_action_screen.log_event(game_event)
        except Exception as e:
            print(f"Error receiving data: {e}")
            break

# Function to transmit equipment ID
def transmit_equipment_id(equipment_id):
    global sock_broadcast
    message = equipment_id
    sock_broadcast.sendto(message.encode(), ('<broadcast>', 7500))  # Broadcast on port 7500
    print(f"Sent Equipment ID: {message}")

# Function to get player info by equipment ID
def get_player_info_by_eq_id(equipment_id):
    cursor = conn.cursor()
    cursor.execute("SELECT id, codename, team FROM players WHERE equipment_id = %s", (equipment_id,))
    result = cursor.fetchone()
    if result:
        return {'id': result[0], 'codename': result[1], 'team': result[2]}
    return None

# Function to handle base scoring
def handle_base_scored(base_color):
    cursor = conn.cursor()
    if base_color == "red":
        # Green team scores
        cursor.execute("SELECT id, codename FROM players WHERE team = 'green'")
        green_players = cursor.fetchall()
        for player in green_players:
            player_id, codename = player
            # Update score
            cursor.execute("UPDATE players SET score = score + 100 WHERE id = %s", (player_id,))
            # Update codename with 'B' if not already present
            if not codename.startswith("B "):
                new_codename = f"B {codename}"
                cursor.execute("UPDATE players SET codename = %s WHERE id = %s", (new_codename, player_id))
        conn.commit()
        if play_action_screen_instance and play_action_screen_instance.is_open:
            play_action_screen_instance.log_event("Green base scored by Red team!")
    elif base_color == "green":
        # Red team scores
        cursor.execute("SELECT id, codename FROM players WHERE team = 'red'")
        red_players = cursor.fetchall()
        for player in red_players:
            player_id, codename = player
            # Update score
            cursor.execute("UPDATE players SET score = score + 100 WHERE id = %s", (player_id,))
            # Update codename with 'B' if not already present
            if not codename.startswith("B "):
                new_codename = f"B {codename}"
                cursor.execute("UPDATE players SET codename = %s WHERE id = %s", (new_codename, player_id))
        conn.commit()
        if play_action_screen_instance and play_action_screen_instance.is_open:
            play_action_screen_instance.log_event("Red base scored by Green team!")

# Function to clear the database
def clear_database(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players")
    conn.commit()
    print("Database cleared.")
    messagebox.showinfo("Success", "Database has been cleared.")

# View database function
def show_database_menu_tk(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, codename, team FROM players ORDER BY codename ASC")
    entries = cursor.fetchall()

    database_window = tk.Toplevel(root)
    database_window.title("Player Database")

    for i, (player_id, codename, team) in enumerate(entries):
        tk.Label(database_window, text=f"ID: {player_id} | Codename: {codename} | Team: {team}").grid(row=i, column=0, padx=5, pady=2)
        tk.Button(database_window, text="Delete", command=lambda pid=player_id: delete_player(pid, conn)).grid(row=i, column=1, padx=5, pady=2)

# Function to add a new player through a Tkinter dialog
def add_new_player_tk(conn):
    codename = simpledialog.askstring("Input", "Enter New Codename:")
    if codename:
        team = simpledialog.askstring("Input", "Enter Team (red/blue):")
        if team and team.lower() in ['red', 'blue']:
            team = team.lower()
            cursor = conn.cursor()
            while True:
                new_id = random.randint(1, 9999)  # Generate a new ID between 1 and 9999
                cursor.execute("SELECT * FROM players WHERE id = %s", (new_id,))
                if cursor.fetchone() is None:
                    # Assign a unique equipment_id
                    new_eq_id = random.randint(1000, 9999)
                    cursor.execute("SELECT * FROM players WHERE equipment_id = %s", (new_eq_id,))
                    if cursor.fetchone() is None:
                        cursor.execute("INSERT INTO players (id, codename, team, equipment_id, score) VALUES (%s, %s, %s, %s, %s)", 
                                       (new_id, codename, team, new_eq_id, 0))
                        conn.commit()
                        messagebox.showinfo("Success", f"New Player Added: ID={new_id}, Codename={codename}, Team={team}, Equipment ID={new_eq_id}")
                        break
        else:
            messagebox.showwarning("Invalid Team", "Team must be 'red' or 'blue'.")

# Function to delete a player
def delete_player(player_id, conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE id = %s", (player_id,))
    conn.commit()
    messagebox.showinfo("Success", f"Player with ID={player_id} has been deleted.")

# Class for Play Action Screen
class PlayActionScreen:
    def __init__(self, master):
        self.master = master
        self.play_screen = tk.Toplevel(master)
        self.play_screen.title("Play Action Screen")
        self.play_screen.geometry("1000x800")
        self.is_open = True

        # Team Score Areas
        self.frame_red_team = tk.LabelFrame(self.play_screen, text="Red Team Scores", bg="red", fg="white", font=("Arial", 12, "bold"), width=250, height=400)
        self.frame_red_team.grid(row=0, column=0, padx=10, pady=10, sticky="n")

        self.frame_blue_team = tk.LabelFrame(self.play_screen, text="Blue Team Scores", bg="cyan", fg="white", font=("Arial", 12, "bold"), width=250, height=400)
        self.frame_blue_team.grid(row=0, column=2, padx=10, pady=10, sticky="n")

        # Initialize team score labels
        self.red_team_scores = {}
        self.blue_team_scores = {}

        self.setup_team_scores(self.frame_red_team, self.red_team_scores, "red")
        self.setup_team_scores(self.frame_blue_team, self.blue_team_scores, "blue")

        # Game Action Area (Scrollable)
        self.frame_action = tk.LabelFrame(self.play_screen, text="Game Action", bg="black", fg="white", font=("Arial", 12, "bold"), width=500, height=600)
        self.frame_action.grid(row=0, column=1, padx=10, pady=10)

        # Scrollable text widget for game action events
        self.game_action_text = scrolledtext.ScrolledText(self.frame_action, wrap=tk.WORD, width=60, height=30, state='disabled')
        self.game_action_text.pack(padx=10, pady=10)

        # Handle window close
        self.play_screen.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start periodic score update
        self.update_scores()

    def setup_team_scores(self, frame, team_scores_dict, team_color):
        cursor = conn.cursor()
        cursor.execute("SELECT id, codename, score FROM players WHERE team = %s", (team_color,))
        players = cursor.fetchall()
        for player in players:
            player_id, codename, score = player
            label = tk.Label(frame, text=f"{codename}: {score}", bg=frame.cget("bg"), fg="white", font=("Arial", 10))
            label.pack(anchor='w', padx=5, pady=2)
            team_scores_dict[player_id] = label

    def log_event(self, event):
        self.game_action_text.config(state='normal')
        self.game_action_text.insert(tk.END, event + "\n")
        self.game_action_text.see(tk.END)
        self.game_action_text.config(state='disabled')

    def update_scores(self):
        cursor = conn.cursor()
        # Update Red Team Scores
        cursor.execute("SELECT id, codename, score FROM players WHERE team = 'red'")
        red_players = cursor.fetchall()
        for player in red_players:
            player_id, codename, score = player
            if player_id in self.red_team_scores:
                self.red_team_scores[player_id].config(text=f"{codename}: {score}")
            else:
                label = tk.Label(self.frame_red_team, text=f"{codename}: {score}", bg=self.frame_red_team.cget("bg"), fg="white", font=("Arial", 10))
                label.pack(anchor='w', padx=5, pady=2)
                self.red_team_scores[player_id] = label

        # Update Blue Team Scores
        cursor.execute("SELECT id, codename, score FROM players WHERE team = 'blue'")
        blue_players = cursor.fetchall()
        for player in blue_players:
            player_id, codename, score = player
            if player_id in self.blue_team_scores:
                self.blue_team_scores[player_id].config(text=f"{codename}: {score}")
            else:
                label = tk.Label(self.frame_blue_team, text=f"{codename}: {score}", bg=self.frame_blue_team.cget("bg"), fg="white", font=("Arial", 10))
                label.pack(anchor='w', padx=5, pady=2)
                self.blue_team_scores[player_id] = label

        # Schedule the next update
        self.play_screen.after(1000, self.update_scores)

    def on_close(self):
        self.is_open = False
        self.stop_music()
        self.play_screen.destroy()

# Function to show the Play Action Screen
def show_play_action_screen():
    global play_action_screen_instance
    if play_action_screen_instance is None or not play_action_screen_instance.is_open:
        play_action_screen_instance = PlayActionScreen(root)
        # Start the listener thread with the new play action screen
        listener_thread = threading.Thread(target=listen_for_data, args=(sock_receive, play_action_screen_instance), daemon=True)
        listener_thread.start()
        # Start the game countdown
        start_game_countdown(play_action_screen_instance)
    else:
        play_action_screen_instance.play_screen.lift()

# Function to start game countdown
def start_game_countdown(play_action_screen):
    pygame.mixer.init()
    pygame.mixer.music.load("Track07.mp3") #THIS IS HARDCODED 
    countdown_window = tk.Toplevel(root)
    countdown_window.title("Game Starting")
    countdown_window.geometry("300x200")
    countdown_window.configure(bg='black')

    label = tk.Label(countdown_window, text="Game Starting in:", bg='black', fg='white', font=("Arial", 16))
    label.pack(pady=20)

    countdown_label = tk.Label(countdown_window, text="5", bg='black', fg='white', font=("Arial", 48))
    countdown_label.pack(pady=20)

    def countdown(n):
        if n >= 0:
            countdown_label.config(text=str(n))
            countdown_window.after(1000, countdown, n-1)
        else:
            countdown_window.destroy()
            # Send code 202 to start the game
            sock_broadcast.sendto('202'.encode(), ('<broadcast>', 7500))
            play_action_screen.log_event("Game Started!")
    
    # Start playing the music 5 seconds before the countdown starts
    def start_music():
        pygame.mixer.music.play(-1) # Loop the music
    
    # Schedule the music to start 5 seconds before the countdown
    countdown_window.after(5000, start_music)

    countdown(5)

# Function to end the game
def end_game(play_action_screen):
    for _ in range(3):
        sock_broadcast.sendto('221'.encode(), ('<broadcast>', 7500))
        print("Sent: 221")
        play_action_screen.log_event("Game Ended!")
        time.sleep(1)  # Brief pause between sends
    pygame.mixer.music.stop()  # Stop the music

# Function to handle base scoring
def handle_base_scored(base_color):
    cursor = conn.cursor()
    if base_color == "red":
        # Green team scores
        cursor.execute("SELECT id, codename FROM players WHERE team = 'green'")
        green_players = cursor.fetchall()
        for player in green_players:
            player_id, codename = player
            # Update score
            cursor.execute("UPDATE players SET score = score + 100 WHERE id = %s", (player_id,))
            # Update codename with 'B' if not already present
            if not codename.startswith("B "):
                new_codename = f"B {codename}"
                cursor.execute("UPDATE players SET codename = %s WHERE id = %s", (new_codename, player_id))
        conn.commit()
        if play_action_screen_instance and play_action_screen_instance.is_open:
            play_action_screen_instance.log_event("Green base scored by Red team!")
    elif base_color == "green":
        # Red team scores
        cursor.execute("SELECT id, codename FROM players WHERE team = 'red'")
        red_players = cursor.fetchall()
        for player in red_players:
            player_id, codename = player
            # Update score
            cursor.execute("UPDATE players SET score = score + 100 WHERE id = %s", (player_id,))
            # Update codename with 'B' if not already present
            if not codename.startswith("B "):
                new_codename = f"B {codename}"
                cursor.execute("UPDATE players SET codename = %s WHERE id = %s", (new_codename, player_id))
        conn.commit()

        if play_action_screen_instance and play_action_screen_instance.is_open:
            play_action_screen_instance.log_event("Red base scored by Green team!")

# Function to check if at least one player on each team
def validate_players():
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM players WHERE team = 'red'")
    red_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM players WHERE team = 'blue'")
    blue_count = cursor.fetchone()[0]
    return red_count >= 1 and blue_count >= 1

# Function to close the program gracefully
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

# Main Tkinter Frame
root = tk.Tk()
root.withdraw()  # Hide the main window initially

# Show the splash screen and run the main window after it closes
show_splash_screen()
root.after(3000, start_main_window)  # After 3 seconds, show the main window

# Set up database connection first
conn = connect_to_database()  # Ensure database is connected first

# Then set up broadcast and receive sockets
sock_broadcast = setup_udp_broadcast_socket()  # Broadcast socket on port 7500
sock_receive = setup_udp_receive_socket()      # Receive socket on port 7501

# Initialize the Play Action Screen instance
play_action_screen_instance = None

# Setup main window
root.deiconify()  # Show the main window

root.title("Photon Laser Tag Setup")
root.geometry("1000x800")
root.protocol("WM_DELETE_WINDOW", on_closing)

# Create a canvas to draw the background
canvas = tk.Canvas(root, width=1000, height=800, bg='black')
canvas.pack()

# Function for generating dynamic background
def draw_background(canvas):
    canvas.delete("all")
    for _ in range(30):
        start_pos = (random.randint(0, 1000), random.randint(0, 800))
        end_pos = (random.randint(0, 1000), random.randint(0, 800))
        canvas.create_line(start_pos, end_pos, fill="red", width=2)
    canvas.after(800, draw_background, canvas)

# Start drawing the background
draw_background(canvas)

# Team Entry Forms
frame = tk.Frame(root, bg='black')
frame.place(relx=0.5, rely=0.4, anchor='center')

team1_entries = create_input_form(frame, "Red Team", "red", 0, 0, conn, sock_broadcast, play_action_screen_instance)
team2_entries = create_input_form(frame, "Blue Team", "cyan", 0, 4, conn, sock_broadcast, play_action_screen_instance)

# Buttons
button_frame = tk.Frame(root, bg='black')

add_player_button = tk.Button(button_frame, text="Add New Player", command=lambda: add_new_player_tk(conn), width=15)
add_player_button.grid(row=0, column=1, padx=10, pady=5)

view_db_button = tk.Button(button_frame, text="View Player Database", command=lambda: show_database_menu_tk(conn), width=20)
view_db_button.grid(row=0, column=2, padx=10, pady=5)

clear_db_button = tk.Button(button_frame, text="Clear Database", command=lambda: clear_database(conn), width=15)
clear_db_button.grid(row=0, column=3, padx=10, pady=5)

# Start Game Button
start_game_button = tk.Button(button_frame, text="Start Game", command=show_play_action_screen, width=20, bg='green', fg='white')
start_game_button.grid(row=0, column=4, padx=10, pady=5)

button_frame.place(relx=0.5, rely=0.9, anchor='center')

root.mainloop()

