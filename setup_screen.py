# setup_screen.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import random

class SetupScreen:
    def __init__(self, parent, database, udp_comm, start_game_callback):
        self.parent = parent
        self.database = database
        self.udp_comm = udp_comm
        self.start_game_callback = start_game_callback

        self.frame = tk.Frame(parent, bg='black')
        self.frame.pack(expand=True, fill='both')

        # Lists to store team players as tuples of (equipment_id, codename)
        self.red_team_players = []
        self.blue_team_players = []

        self.create_widgets()

    def create_widgets(self):
        # Canvas for background animation
        self.canvas = tk.Canvas(self.frame, width=1000, height=800, bg='black')
        self.canvas.pack()

        # Start drawing the background
        self.draw_background()

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
            text="Clear Database",
            command=self.clear_database,
            width=15
        )
        self.clear_db_button.grid(row=0, column=2, padx=10, pady=5)

        self.start_game_button = tk.Button(
            self.button_frame,
            text="Start Game",
            command=self.start_game,
            width=20,
            bg='green',
            fg='white'
        )
        self.start_game_button.grid(row=0, column=3, padx=10, pady=5)

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

        tk.Label(frame, text="Equipment ID", font=("Arial", 10, "bold"), width=12, bg=color).grid(row=row+1, column=col, padx=5)
        tk.Label(frame, text="Codename", font=("Arial", 10, "bold"), width=10, bg=color).grid(row=row+1, column=col+1, padx=5)
        tk.Label(frame, text="Equipment", font=("Arial", 10, "bold"), width=10, bg=color).grid(row=row+1, column=col+2, padx=5)

        entries = []
        for i in range(15):
            equipment_id_var = tk.StringVar()
            codename_var = tk.StringVar()
            entry_equipment_id = tk.Entry(frame, width=12, textvariable=equipment_id_var)
            entry_codename = tk.Entry(frame, width=10, textvariable=codename_var, state='readonly')
            equipment_combobox = ttk.Combobox(frame, width=5, values=list(range(1, 31)))
            equipment_combobox.set("")  # Set default value

            entry_equipment_id.grid(row=i + row + 2, column=col, padx=5, pady=2)
            entry_codename.grid(row=i + row + 2, column=col + 1, padx=5, pady=2)
            equipment_combobox.grid(row=i + row + 2, column=col + 2, padx=5, pady=2)

            # Bind the update_codename function to equipment ID field updates
            equipment_id_var.trace_add('write', lambda name, index, mode, eid_var=equipment_id_var, cname_var=codename_var: self.update_codename(eid_var, cname_var))

            # Add enter button to validate and broadcast
            enter_button = tk.Button(
                frame,
                text="Enter",
                command=lambda eid_var=equipment_id_var, cname_var=codename_var, equip=equipment_combobox, team=team_players_list: self.validate_and_broadcast(eid_var, cname_var, equip, team),
                width=8
            )
            enter_button.grid(row=i + row + 2, column=col + 3, padx=5, pady=2)

            entries.append((entry_equipment_id, entry_codename, equipment_combobox))

        return entries

    def update_codename(self, equipment_id_var, codename_var):
        equipment_id = equipment_id_var.get()

        # Clear the codename entry field before updating
        codename_var.set("")

        if equipment_id.isdigit():  # Check if the input is numeric
            codename = self.database.get_codename(equipment_id)
            if codename:
                codename_var.set(codename)  # Insert codename
            else:
                codename_var.set("Invalid ID")
        else:
            codename_var.set("")  # Reset for non-numeric input

    def validate_and_broadcast(self, equipment_id_var, codename_var, equipment_combobox, team_players_list):
        equipment_id = equipment_id_var.get()
        codename = codename_var.get()
        equipment_id_selected = equipment_combobox.get()

        if equipment_id and codename != "Invalid ID":
            # Add to team list if not already present
            if codename not in team_players_list:
                team_players_list.append(codename)
        else:
            return

        if equipment_id_selected:
            # Assuming equipment_id_selected is unique and corresponds to a player's equipment ID
            # Update the equipment_id_to_codename mapping here if needed
            pass
        else:
            messagebox.showwarning("Warning", "Equipment ID cannot be empty.")

    def add_new_player(self):
        codename = simpledialog.askstring("Input", "Enter New Codename:", parent=self.parent)
        if codename:
            new_id = self.database.add_player(codename)
            if new_id:
                messagebox.showinfo("Success", f"New Player Added: ID={new_id}, Codename={codename}")
            else:
                messagebox.showerror("Error", "Failed to add new player.")

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

    def start_game(self):
        # Gather Red and Blue team player data
        red_team_players = []
        blue_team_players = []
        equipment_id_to_codename = {}

        # Collect data from Red Team
        for entry in self.red_team_entries:
            equipment_id = entry[0].get()  # Equipment ID entry
            codename = entry[1].get()      # Codename entry
            if equipment_id and codename != "Invalid ID":
                red_team_players.append(codename)
                equipment_id_to_codename[int(equipment_id)] = codename

        # Collect data from Blue Team
        for entry in self.blue_team_entries:
            equipment_id = entry[0].get()  # Equipment ID entry
            codename = entry[1].get()      # Codename entry
            if equipment_id and codename != "Invalid ID":
                blue_team_players.append(codename)
                equipment_id_to_codename[int(equipment_id)] = codename

        # Now start the game by passing the collected team data to the PlayActionScreen
        if red_team_players and blue_team_players:
            PlayActionScreen(self.parent, self.udp_comm, red_team_players, blue_team_players, equipment_id_to_codename)
        else:
            messagebox.showerror("Error", "Both teams must have at least one player to start the game.")

