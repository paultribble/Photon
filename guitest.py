import psycopg2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import socket
import sys
import os
import random

# Connect to the PostgreSQL database
def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname="photon",       # Database name
            user="student",  # PostgreSQL username
            password="student",  # PostgreSQL password
            host="localhost",      # Hostname
            port="5432"            # Default PostgreSQL port
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        sys.exit(1)

def generate_unique_id(cursor):
    while True:
        new_id = random.randint(1, 999999)
        cursor.execute("SELECT id FROM player WHERE id = %s", (new_id,))
        if cursor.fetchone() is None:
            return new_id

def show_splash_screen(root, splash_duration=3000):
    splash = tk.Toplevel()
    splash.overrideredirect(True)
    splash.geometry("1200x800")  # Size of the splash screen
    
    def resize_image(event):
        splash_width = event.width
        splash_height = event.height
        image_ratio = image.width / image.height
        splash_ratio = splash_width / splash_height
        if image_ratio > splash_ratio:
            new_width = splash_width
            new_height = int(splash_width / image_ratio)
        else:
            new_height = splash_height
            new_width = int(splash_height * image_ratio)
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)
        logo = ImageTk.PhotoImage(resized_image)
        label.config(image=logo)
        label.image = logo

    script_dir = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(script_dir, "Images", "logo.jpg")
    image = Image.open(logo_path)
    
    label = tk.Label(splash)
    label.pack(expand=True, fill=tk.BOTH)
    splash.bind("<Configure>", resize_image)
    
    root.after(splash_duration, splash.destroy)  # Close splash after the duration

def player_entry_screen(root, conn):
    cursor = conn.cursor()

    # Team variables
    team1_name = tk.StringVar(value="Blue Team")
    team2_name = tk.StringVar(value="Red Team")

    def get_team_color(team_name):
        color_map = {
            "Blue Team": "lightblue",
            "Red Team": "lightcoral"
        }
        return color_map.get(team_name, "white")

    def update_team_names_and_colors(*args):
        team1_label.config(text=team1_name.get(), background=get_team_color(team1_name.get()))
        team2_label.config(text=team2_name.get(), background=get_team_color(team2_name.get()))

    team1_name.trace_add("write", update_team_names_and_colors)
    team2_name.trace_add("write", update_team_names_and_colors)

    def query_player_data(player_id):
        try:
            cursor.execute("SELECT codename FROM player WHERE id = %s", (player_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error querying player data: {e}")
            return None

    def save_player_data(player_id, nickname):
        try:
            cursor = conn.cursor()
            # Check if the player already exists
            cursor.execute("SELECT id FROM player WHERE id = %s", (player_id,))
            if cursor.fetchone() is None:
                # Player does not exist, insert new record
                cursor.execute(
                    "INSERT INTO player (id, codename) VALUES (%s, %s)",
                    (player_id, nickname)
                )
            else:
                # Player exists, update existing record
                cursor.execute(
                    "UPDATE player SET codename = %s WHERE id = %s",
                    (nickname, player_id)
                )
            conn.commit()
        except Exception as e:
            print(f"Error saving player data: {e}")

    def handle_entry(team_number, row):
        player_id = player_id_entries[team_number][row].get()
        nickname = nickname_entries[team_number][row].get()

        if player_id:
            existing_nickname = query_player_data(player_id)
            if existing_nickname:
                # Display existing nickname if found
                nickname_entries[team_number][row].set(existing_nickname)
            elif nickname:
                # Save new player data
                save_player_data(player_id, nickname)
            else:
                nickname_entries[team_number][row].set("Enter a nickname")

    def start_game():
        print("Starting game...")
        # You can add logic to switch to the play action screen here

    def generate_id_for_team(team_number):
        unique_id = generate_unique_id(cursor)
        player_id_entries[team_number][0].delete(0, tk.END)
        player_id_entries[team_number][0].insert(0, unique_id)

    def open_manage_players(conn):
        manage_players_window = tk.Toplevel()
        manage_players_window.title("Manage Players")

        columns = ("ID", "Nickname")
        tree = ttk.Treeview(manage_players_window, columns=columns, show="headings")
        tree.heading("ID", text="Player ID")
        tree.heading("Nickname", text="Nickname")
        tree.pack(fill=tk.BOTH, expand=True)

        def load_players():
            cursor = conn.cursor()
            cursor.execute("SELECT id, codename FROM player")
            for row in cursor.fetchall():
                tree.insert("", tk.END, values=row)

        load_players()

        tk.Button(manage_players_window, text="Add New Player", command=lambda: add_new_player_popup(conn)).pack(pady=5)
        tk.Button(manage_players_window, text="Close", command=manage_players_window.destroy).pack(pady=5)

    def add_new_player_popup(conn):
        def save_new_player():
            player_id = id_entry.get()
            nickname = nickname_entry.get()
            if nickname:
                try:
                    cursor = conn.cursor()
                    # Generate unique ID
                    if player_id:
                        player_id = int(player_id)
                    else:
                        player_id = generate_unique_id(cursor)
                    # Save new player data
                    cursor.execute(
                        "INSERT INTO player (id, codename) VALUES (%s, %s) ON CONFLICT (id) DO UPDATE SET codename = EXCLUDED.codename",
                        (player_id, nickname)
                    )
                    conn.commit()
                    new_player_popup.destroy()
                except Exception as e:
                    print(f"Error saving new player: {e}")

        new_player_popup = tk.Toplevel()
        new_player_popup.title("Add New Player")

        tk.Label(new_player_popup, text="Player ID (Leave empty for auto-generate):").pack(padx=10, pady=5)
        id_entry = tk.Entry(new_player_popup)
        id_entry.pack(padx=10, pady=5)

        tk.Label(new_player_popup, text="Nickname:").pack(padx=10, pady=5)
        nickname_entry = tk.Entry(new_player_popup)
        nickname_entry.pack(padx=10, pady=5)

        tk.Button(new_player_popup, text="Save", command=save_new_player).pack(pady=10)

    # Setup the entry form for two teams
    team1_frame = ttk.Frame(root, padding=10, style="Team.TFrame")
    team1_frame.grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
    team2_frame = ttk.Frame(root, padding=10, style="Team.TFrame")
    team2_frame.grid(row=0, column=1, padx=10, pady=5, sticky="nsew")

    team1_label = ttk.Label(team1_frame, text="Player ID", background=get_team_color(team1_name.get()), font=('Helvetica', 10, 'bold'))
    team1_label.grid(row=0, column=0, padx=5, pady=2)
    ttk.Label(team1_frame, text="Nickname", background=get_team_color(team1_name.get()), font=('Helvetica', 10, 'bold')).grid(row=0, column=1, padx=5, pady=2)
    
    team2_label = ttk.Label(team2_frame, text="Player ID", background=get_team_color(team2_name.get()), font=('Helvetica', 10, 'bold'))
    team2_label.grid(row=0, column=0, padx=5, pady=2)
    ttk.Label(team2_frame, text="Nickname", background=get_team_color(team2_name.get()), font=('Helvetica', 10, 'bold')).grid(row=0, column=1, padx=5, pady=2)

    player_id_entries = [[], []]
    nickname_entries = [[], []]

    for i in range(15):
        player_id_entry1 = ttk.Entry(team1_frame)
        player_id_entry1.grid(row=i+1, column=0, padx=5, pady=2)
        nickname_entry1 = ttk.Entry(team1_frame)
        nickname_entry1.grid(row=i+1, column=1, padx=5, pady=2)
        player_id_entries[0].append(player_id_entry1)
        nickname_entries[0].append(nickname_entry1)

        player_id_entry2 = ttk.Entry(team2_frame)
        player_id_entry2.grid(row=i+1, column=0, padx=5, pady=2)
        nickname_entry2 = ttk.Entry(team2_frame)
        nickname_entry2.grid(row=i+1, column=1, padx=5, pady=2)
        player_id_entries[1].append(player_id_entry2)
        nickname_entries[1].append(nickname_entry2)

    submit_button = tk.Button(root, text="Submit", command=lambda: [handle_entry(0, i) for i in range(15)] + [handle_entry(1, i) for i in range(15)])
    submit_button.grid(row=1, column=0, padx=5, pady=5)

    start_game_button = tk.Button(root, text="Start Game", command=start_game)
    start_game_button.grid(row=1, column=1, padx=5, pady=5)

    manage_players_button = tk.Button(root, text="Manage Players", command=lambda: open_manage_players(conn))
    manage_players_button.grid(row=2, column=0, columnspan=2, pady=5)

def main():
    conn = connect_to_database()
    root = tk.Tk()
    root.title("Laser Tag Player Entry System")
    show_splash_screen(root)
    root.after(3000, lambda: player_entry_screen(root, conn))
    root.mainloop()

if __name__ == "__main__":
    main()
