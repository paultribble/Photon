import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import psycopg2
import sys
import os

# Connect to the PostgreSQL database
def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname="photon",       # Database name
            user="student",        # Your PostgreSQL username
            password="student",    # Your PostgreSQL password
            host="localhost",      # Hostname
            port="5432"            # Default PostgreSQL port
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        sys.exit(1)

# Function to list all players
def list_all_players(conn):
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, codename FROM players")
        players = cursor.fetchall()
        print("List of Players:")
        for player in players:
            print(f"ID: {player[0]}, Codename: {player[1]}")
    except Exception as e:
        print(f"Error retrieving players: {e}")

# Create splash screen
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

# Player entry screen
def player_entry_screen(root, conn):
    cursor = conn.cursor()

    def query_player_data(player_id):
        try:
            cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error querying player data: {e}")
            return None

    def save_player_data(player_id, nickname):
        try:
            cursor.execute(
                "INSERT INTO players (id, codename) VALUES (%s, %s)",
                (player_id, nickname)
            )
            conn.commit()
        except psycopg2.IntegrityError:
            conn.rollback()
            cursor.execute(
                "UPDATE players SET codename = %s WHERE id = %s",
                (nickname, player_id)
            )
            conn.commit()
        except Exception as e:
            print(f"Error saving player data: {e}")

    def handle_entry(event=None):
        # Logic to handle data entry will be modified to accommodate both teams
        pass  # We will update this function later

    # Main frame
    main_frame = tk.Frame(root, bg="lightgray")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Team Name Entries with Labels
    team1_name_var = tk.StringVar(value="Blue Team")
    team2_name_var = tk.StringVar(value="Red Team")

    ttk.Label(main_frame, text="Team 1:", background="lightgray", font=('Arial', 12)).grid(row=0, column=0, padx=10, pady=5, sticky="e")
    ttk.Entry(main_frame, textvariable=team1_name_var, font=('Arial', 14, 'bold')).grid(row=0, column=1, pady=5, columnspan=2)

    ttk.Label(main_frame, text="Team 2:", background="lightgray", font=('Arial', 12)).grid(row=0, column=4, padx=10, pady=5, sticky="e")
    ttk.Entry(main_frame, textvariable=team2_name_var, font=('Arial', 14, 'bold')).grid(row=0, column=5, pady=5, columnspan=2)

    # Labels for Player ID and Codename Fields
    ttk.Label(main_frame, text="Player ID", background="lightgray").grid(row=1, column=1, padx=10, pady=5)
    ttk.Label(main_frame, text="Codename", background="lightgray").grid(row=1, column=2, padx=10, pady=5)
    ttk.Label(main_frame, text="Player ID", background="lightgray").grid(row=1, column=5, padx=10, pady=5)
    ttk.Label(main_frame, text="Codename", background="lightgray").grid(row=1, column=4, padx=10, pady=5)

    # Labels for Player Numbers and Entry Fields
    for i in range(15):
        player_num = i + 1
        ttk.Label(main_frame, text=f"{player_num}.", background="lightgray").grid(row=player_num+2, column=0, padx=10, pady=5, sticky="e")
        ttk.Label(main_frame, text=f"{player_num}.", background="lightgray").grid(row=player_num+2, column=6, padx=10, pady=5, sticky="w")

        # Blue Team Entries
        player_id_entry_blue = ttk.Entry(main_frame)
        player_id_entry_blue.grid(row=player_num+2, column=1, padx=10, pady=5)
        
        nickname_var_blue = tk.StringVar()
        nickname_entry_blue = ttk.Entry(main_frame, textvariable=nickname_var_blue)
        nickname_entry_blue.grid(row=player_num+2, column=2, padx=10, pady=5)
        
        # Red Team Entries
        player_id_entry_red = ttk.Entry(main_frame)
        player_id_entry_red.grid(row=player_num+2, column=5, padx=10, pady=5)
        
        nickname_var_red = tk.StringVar()
        nickname_entry_red = ttk.Entry(main_frame, textvariable=nickname_var_red)
        nickname_entry_red.grid(row=player_num+2, column=4, padx=10, pady=5)

    # Submit Buttons for Each Team
    submit_button_blue = ttk.Button(main_frame, text=f"Submit {team1_name_var.get()}", command=handle_entry)
    submit_button_blue.grid(row=18, column=1, columnspan=2, pady=10)

    submit_button_red = ttk.Button(main_frame, text=f"Submit {team2_name_var.get()}", command=handle_entry)
    submit_button_red.grid(row=18, column=4, columnspan=2, pady=10)

    # Function to update the submit buttons dynamically based on team names
    def update_submit_buttons(*args):
        submit_button_blue.config(text=f"Submit {team1_name_var.get()}")
        submit_button_red.config(text=f"Submit {team2_name_var.get()}")

    team1_name_var.trace("w", update_submit_buttons)
    team2_name_var.trace("w", update_submit_buttons)

    # Start Game Button
    def start_game():
        print("Starting game...")
        # You can add logic to switch to the play action screen here

    ttk.Button(main_frame, text="Start Game", command=start_game).grid(row=19, column=2, columnspan=3, pady=20)

# Main function
def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window during the splash screen

    show_splash_screen(root)  # Show splash screen

    # Database connection
    conn = connect_to_database()

    # List all players after establishing connection
    list_all_players(conn)

    root.after(3100, lambda: [root.deiconify(), player_entry_screen(root, conn)])  # Show player entry screen after splash

    root.title("Laser Tag Player Entry")
    root.geometry("800x600")  # Adjust size as needed
    root.minsize(800, 600)  # Set a minimum size

    # Bind the "q" key to quit the program
    root.bind("q", lambda event: [conn.close(), root.destroy()])

    root.mainloop()

if __name__ == "__main__":
    main()

