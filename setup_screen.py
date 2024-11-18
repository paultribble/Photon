# setup_screen.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random
import os
from PIL import Image, ImageTk
import pygame
from pynput import keyboard
import play_action_screen as PlayActionScreen

music_on = True
class SetupScreen:
    # Class attribute to store the single instance of the SetupScreen (used for music)
    instance = None

    def __init__(self, parent, database, udp_comm):
        self.parent = parent
        self.database = database
        self.udp_comm = udp_comm

        # Initialize Pygame mixer for sound effects
        pygame.mixer.init()

        SetupScreen.instance = self  # Store the instance for music control

        self.frame = tk.Frame(parent, bg='black')
        self.frame.pack(expand=True, fill='both')

        # Countdown label (in Toplevel window)
        self.countdown_window = None
        self.countdown_label = None
        
        # Lists to store team players
        self.red_team_players = []
        self.blue_team_players = []

        self.create_widgets()
        self.start_key_listener()
         
        self.frame.update_idletasks()
        
    def create_widgets(self):
        # Canvas for background animation
        self.canvas = tk.Canvas(self.frame, width=1000, height=800, bg='black')
        self.canvas.pack()

        # Start drawing the background
        self.draw_background()
        
        # Countdown label
        self.countdown_label = tk.Label(self.frame, text="", bg='black', fg='white', font=("Arial", 48))
        self.countdown_label.place(relx=0.5, rely=0.3, anchor='center')

        # Team Entry Forms
        self.team_frame = tk.Frame(self.frame, bg='black')
        self.team_frame.place(relx=0.5, rely=0.4, anchor='center')

        self.red_team_entries = self.create_input_form(
            self.team_frame, "Red Team", "red", 0, 0, self.red_team_players
        )
        self.blue_team_entries = self.create_input_form(
            self.team_frame, "Blue Team", "cyan", 0, 4, self.blue_team_players
        )

        # Buttons Frame
        self.button_frame = tk.Frame(self.frame, bg='black')
        self.button_frame.place(relx=0.5, rely=0.9, anchor='center')

        self.add_player_button = tk.Button(
            self.button_frame,
            text="Add New Player",
            command=self.add_new_player,
            width=15
        )
        self.add_player_button.grid(row=0, column=0, padx=10, pady=5)

        self.view_db_button = tk.Button(
            self.button_frame,
            text="View Player Database",
            command=self.view_player_database,
            width=20
        )
        self.view_db_button.grid(row=0, column=1, padx=10, pady=5)

        self.clear_db_button = tk.Button(
            self.button_frame,
            text="Clear Players (F12)",
            command=self.clear_current_players,  # Updated to clear current players
            width=15
        )
        self.clear_db_button.grid(row=0, column=2, padx=10, pady=5)

        self.start_game_button = tk.Button(
            self.button_frame,
            text="Start Game (F5)",
            command=self.initiate_countdown,
            width=20,
            bg='green',
            fg='white'
        )
        self.start_game_button.grid(row=0, column=3, padx=10, pady=5)

    
    def play_music(self):

        tracks = [
            "Track01.mp3",
            "Track02.mp3",
            "Track03.mp3",
            "Track04.mp3",
            "Track05.mp3",
            "Track06.mp3",
            "Track07.mp3"
        ]

        # Randomly select a track
        selected_track = random.choice(tracks)

        # Load and play the selected track
        pygame.mixer.music.load(selected_track)
        if music_on:
            pygame.mixer.music.play()  #Play the track once
            print(f"Playing: {selected_track}")
        else:
            print("Stopping music...")
            pygame.mixer.music.stop() # Stop the background music

    def draw_background(self):
        self.canvas.delete("all")
        for _ in range(30):
            start_pos = (random.randint(0, 1000), random.randint(0, 800))
            end_pos = (random.randint(0, 1000), random.randint(0, 800))
            self.canvas.create_line(start_pos, end_pos, fill="red", width=2)
        self.canvas.after(800, self.draw_background)

    def create_input_form(self, frame, team_name, color, row, col, team_players_list):
        team_label = tk.Label(frame, text=team_name, bg=color, font=("Arial", 12, "bold"), width=10)
        team_label.grid(row=row, column=col, padx=10)

        tk.Label(frame, text="ID", font=("Arial", 10, "bold"), width=8, bg=color).grid(row=row+1, column=col, padx=5)
        tk.Label(frame, text="Codename", font=("Arial", 10, "bold"), width=10, bg=color).grid(row=row+1, column=col+1, padx=5)
        tk.Label(frame, text="Equipment", font=("Arial", 10, "bold"), width=10, bg=color).grid(row=row+1, column=col+2, padx=5)

        entries = []
        for i in range(15):
            player_id_var = tk.StringVar()
            entry_id = tk.Entry(frame, width=8, textvariable=player_id_var)
            entry_codename = tk.Entry(frame, width=15, state='readonly')
            equipment_combobox = ttk.Combobox(frame, width=5, values=list(range(1, 31)))
            equipment_combobox.set("")  # Set default value

            entry_id.grid(row=i + row + 2, column=col, padx=5, pady=2)
            entry_codename.grid(row=i + row + 2, column=col + 1, padx=5, pady=2)
            equipment_combobox.grid(row=i + row + 2, column=col + 2, padx=5, pady=2)

            # Bind the update_codename function to player ID field updates
            player_id_var.trace_add('write', lambda name, index, mode, pid_var=player_id_var, codename=entry_codename: self.update_codename(pid_var, codename, self.database))

            # Add enter button to validate and broadcast
            enter_button = tk.Button(
                frame,
                text="Enter",
                command=lambda pid_var=player_id_var, codename=entry_codename, equip=equipment_combobox, team=team_players_list: self.validate_and_broadcast(pid_var, codename, equip, team),
                width=8
            )
            enter_button.grid(row=i + row + 2, column=col + 3, padx=5, pady=2)

            entries.append((entry_id, entry_codename, equipment_combobox))

        return entries

    def update_codename(self, player_id_var, codename_entry, database):
        player_id = player_id_var.get()

        # Clear the codename entry field before updating
        codename_entry.config(state='normal')
        codename_entry.delete(0, tk.END)

        if player_id.isdigit():  # Check if the input is numeric
            codename = database.get_codename(player_id)
            if codename:
                codename_entry.insert(0, codename)  # Insert codename
                codename_entry.config(fg='gray')    # Set text color to gray
            else:
                codename_entry.insert(0, "Invalid ID")
                codename_entry.config(fg='gray')  # Set text color to gray
        else:
            codename_entry.config(fg='black')  # Reset color to black for non-numeric input

        codename_entry.config(state='readonly')

    def validate_and_broadcast(self, player_id_var, codename_entry, equipment_combobox, team):
        player_id = player_id_var.get()
        equipment_id = equipment_combobox.get()

        if player_id and equipment_id:
            codename = self.database.get_codename(player_id)
            if codename:
                player = {
                    'id': int(player_id),
                    'codename': codename,
                    'equipment_id': int(equipment_id),
                    'score': 0  # Initialize score to 0
                }
                # Add player to team if not already present
                if player not in team:
                    team.append(player)

                codename_entry.config(state='normal')
                codename_entry.delete(0, tk.END)
                codename_entry.insert(0, codename)
                codename_entry.config(state='readonly')
                codename_entry.config(fg='black')
            
                # Send equipment ID as confirmation broadcast
                self.udp_comm.send_broadcast(f"{equipment_id}")
                print(f"Added: {player}")
            else:
                codename_entry.insert(0, "Invalid ID")
                codename_entry.config(fg='gray')

    def add_new_player(self):
        # Create a new top-level window for entering player details
        new_player_window = tk.Toplevel(self.parent)
        new_player_window.title("Add New Player")

        tk.Label(new_player_window, text="Enter Player ID (Leave blank for random):").pack(pady=5)
        id_entry = tk.Entry(new_player_window, width=20)
        id_entry.pack(pady=5)

        tk.Label(new_player_window, text="Enter Codename:").pack(pady=5)
        codename_entry = tk.Entry(new_player_window, width=20)
        codename_entry.pack(pady=5)

        def save_player():
            player_id = id_entry.get().strip()
            codename = codename_entry.get().strip()

        # If ID is empty, generate a random ID
            if player_id == "":
                player_id = None  # Will be generated randomly
            else:
             # Validate player ID input
                if not player_id.isdigit():
                    messagebox.showerror("Error", "Player ID must be numeric.")
                    return
                player_id = int(player_id)

            # Try to add the player to the database
            new_id = self.database.add_player(codename, player_id)
            if new_id:
                messagebox.showinfo("Success", f"New Player Added: ID={new_id}, Codename={codename}")
                new_player_window.destroy()  # Close the window
            else:
                messagebox.showerror("Error", "Failed to add new player.")

        save_button = tk.Button(new_player_window, text="Save Player", command=save_player)
        save_button.pack(pady=10)


    def view_player_database(self):
        from database_screen import DatabaseScreen
        DatabaseScreen(self.parent, self.database)

    def clear_database(self):
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to clear the database?")
        if confirm:
            success = self.database.clear_players()
            if success:
                messagebox.showinfo("Success", "Database has been cleared.")
            else:
                messagebox.showerror("Error", "Failed to clear the database.")

    def clear_current_players(self):
    # Confirm the action to clear players
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to clear the current players?")
        if confirm:
        # Clear both red and blue team players
            self.red_team_players.clear()
            self.blue_team_players.clear()

        # Clear the input fields for both teams
            self.clear_player_entries(self.red_team_entries)
            self.clear_player_entries(self.blue_team_entries)

            messagebox.showinfo("Success", "Current players have been cleared.")

    def clear_player_entries(self, team_entries):
        for entry_id, entry_codename, equipment_combobox in team_entries:
            entry_id.delete(0, tk.END)  # Clear the player ID field
            entry_codename.config(state='normal')
            entry_codename.delete(0, tk.END)  # Clear the codename field
            entry_codename.config(state='readonly')
            equipment_combobox.set("")  # Clear the equipment combo box

    
    
    def initiate_countdown(self):
        self.play_music()  # Play background music
        self.parent.after(5000, self.open_and_start_countdown)  # Start countdown from 10

    def open_and_start_countdown(self):
        self.open_countdown_window()  # Open the countdown window
        self.countdown(10)  # Start countdown from 10
 
    def open_countdown_window(self):
        # Create a new top-level window for the countdown
        self.countdown_window = tk.Toplevel(self.parent)
        self.countdown_window.title("Countdown")
        self.countdown_window.geometry("300x300")  # Set window size
        self.countdown_window.configure(bg='black')  # Set background color

        self.countdown_label = tk.Label(self.countdown_window, text="", bg='black', fg='white', font=("Arial", 48))
        self.countdown_label.pack(expand=True)  # Center label in the window

    def countdown(self, count):
        if count >= 0:  # Start countdown from 1
            # Update label to show current count
            self.countdown_label.config(text=str(count))

            # Load and display the corresponding image
            image_path = os.path.join("Images", f"{count}.tif")  # Construct the image path
            if os.path.isfile(image_path):  # Check if the image file exists
                image = Image.open(image_path)
                image = image.resize((200, 200), Image.LANCZOS)  # Resize for better visibility
                self.current_image = ImageTk.PhotoImage(image)  # Create PhotoImage
                self.countdown_label.config(image=self.current_image)  # Set the label to show the image
                self.countdown_label.image = self.current_image  # Keep a reference to avoid garbage collection
            else:
                print(f"Image not found: {image_path}")
                self.countdown_label.config(image='')  # Clear the image if file not found

            # Schedule the next countdown call
            self.countdown_window.after(1000, self.countdown, count - 1)  # Call countdown every second
        else:
            self.countdown_window.destroy()
            self.countdown_window.after(1000, self.start_game)  # Delay before starting the game
            
    
    
    def start_game(self):
        # Check if both teams have a minimum number of players (e.g., 2)
        min_players = 1  # Define the minimum number of players required per team

        if len(self.red_team_players) < min_players:
            messagebox.showerror("Error", "Red team must have at least {} players.".format(min_players))
            return
        if len(self.blue_team_players) < min_players:
            messagebox.showerror("Error", "Blue team must have at least {} players.".format(min_players))
            return

        # If both teams have enough players, start the game
        self.udp_comm.send_broadcast("202")  # Send the 202 broadcast message
        PlayActionScreen.PlayActionScreen(self.parent, self.udp_comm, self.red_team_players, self.blue_team_players)
        
        
    def start_key_listener(self):
        # Key press event handler
        def on_press(key):
            try:
                if key == keyboard.Key.f5:  # Check for F5 key
                    print("F5 Keybind activated!")
                    self.initiate_countdown()  # Call the start_game method
                elif key == keyboard.Key.f12:  # Check for F12 key
                    print("F12 Keybind activated!")
                    self.clear_database()  # Call the clear_database method
            except Exception as e:
                print(f"Error: {e}")

        # Start the keyboard listener
        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()  # Start listening for key presses

    def stop_key_listener(self):
        # Stop the keyboard listener when exiting or switching screens
        if self.listener:
            self.listener.stop()

    def stop_music(self):
        music_on = False
        print("Stopping music...")
        pygame.mixer.music.stop() # Stop the background music
        #set music bool to false, make bool accessible in function where
        #play music is declared