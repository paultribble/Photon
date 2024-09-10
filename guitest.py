import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import socket
import sys
import os
import psycopg2

# Connect to the PostgreSQL database
def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname="photon",       # Database name
            user="student",  # Your PostgreSQL username
            password="student",  # Your PostgreSQL password
            host="localhost",      # Hostname
            port="5432"            # Default PostgreSQL port
        )
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        sys.exit(1)

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

def get_team_color(team_name):
    # Determine the team color based on the first word in the team name
    color_mapping = {
        "Blue": "lightblue",
        "Red": "lightcoral",
        "Green": "lightgreen",
        "Yellow": "lightyellow",
        "Orange": "lightorange",
        "Purple": "lightpurple"
    }
    first_word = team_name.split()[0]
    return color_mapping.get(first_word, "lightgray")  # Default to lightgray if not found

def player_entry_screen(root, conn):
    cursor = conn.cursor()

    # Team variables
    team1_name = tk.StringVar(value="Blue Team")
    team2_name = tk.StringVar(value="Red Team")

    def update_team_labels():
        # Update Team 1
        team1_color = get_team_color(team1_name.get())
        team1_label.config(text=team1_name.get(), background=team1_color)
        # Update Team 2
        team2_color = get_team_color(team2_name.get())
        team2_label.config(text=team2_name.get(), background=team2_color)
        # Update column backgrounds
        columns[0].config(background=team1_color)
        columns[1].config(background=team2_color)

    # Bind variables to update function
    team1_name.trace_add("write", lambda *args: update_team_labels())
    team2_name.trace_add("write", lambda *args: update_team_labels())

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
                "INSERT INTO players (id, codename) VALUES (%s, %s) ON CONFLICT (id) DO UPDATE SET codename = EXCLUDED.codename",
                (player_id, nickname)
            )
            conn.commit()
        except Exception as e:
            print(f"Error saving player data: {e}")

    def handle_entry(event=None):
        player_id = player_id_entry.get()
        nickname = nickname_entry.get()

        if player_id:
            existing_nickname = query_player_data(player_id)
            if existing_nickname:
                nickname_var.set(existing_nickname)
            elif nickname:
                save_player_data(player_id, nickname)
            else:
                nickname_var.set("Enter a nickname")

    def broadcast_equipment_id(equipment_id):
        try:
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_socket.sendto(str(equipment_id).encode(), ("<broadcast>", 7500))
        except Exception as e:
            print(f"Error broadcasting equipment ID: {e}")
        finally:
            udp_socket.close()

    # Main frame
    main_frame = tk.Frame(root, bg="lightgray")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Team 1 UI
    ttk.Label(main_frame, text="Team 1 Name:", background="lightgray").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    team1_name_entry = ttk.Entry(main_frame, textvariable=team1_name)
    team1_name_entry.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(main_frame, text="Team 2 Name:", background="lightgray").grid(row=0, column=2, padx=10, pady=5, sticky="e")
    team2_name_entry = ttk.Entry(main_frame, textvariable=team2_name)
    team2_name_entry.grid(row=0, column=3, padx=10, pady=5)

    team1_label = ttk.Label(main_frame, text=team1_name.get(), background=get_team_color(team1_name.get()), font=('Helvetica', 16, 'bold'))
    team1_label.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

    team2_label = ttk.Label(main_frame, text=team2_name.get(), background=get_team_color(team2_name.get()), font=('Helvetica', 16, 'bold'))
    team2_label.grid(row=1, column=2, columnspan=2, pady=10, sticky="ew")

    # Headers for Player ID and Nickname
    ttk.Label(main_frame, text="Player ID", background="lightgray", font=('Helvetica', 12, 'bold')).grid(row=2, column=0, padx=10, pady=5, sticky="ew")
    ttk.Label(main_frame, text="Nickname", background="lightgray", font=('Helvetica', 12, 'bold')).grid(row=2, column=1, padx=10, pady=5, sticky="ew")

    ttk.Label(main_frame, text="Player ID", background="lightgray", font=('Helvetica', 12, 'bold')).grid(row=2, column=2, padx=10, pady=5, sticky="ew")
    ttk.Label(main_frame, text="Nickname", background="lightgray", font=('Helvetica', 12, 'bold')).grid(row=2, column=3, padx=10, pady=5, sticky="ew")

    columns = [tk.Frame(main_frame, bg=get_team_color(team1_name.get())), tk.Frame(main_frame, bg=get_team_color(team2_name.get()))]
    columns[0].grid(row=3, column=0, columnspan=2, sticky="nsew")
    columns[1].grid(row=3, column=2, columnspan=2, sticky="nsew")

    for i in range(15):
        ttk.Entry(columns[0]).grid(row=i, column=0, padx=5, pady=2)
        ttk.Entry(columns[0]).grid(row=i, column=1, padx=5, pady=2)
        ttk.Entry(columns[1]).grid(row=i, column=2, padx=5, pady=2)
        ttk.Entry(columns[1]).grid(row=i, column=3, padx=5, pady=2)

    ttk.Label(columns[0], text="Player ID", background=get_team_color(team1_name.get()), font=('Helvetica', 10, 'bold')).grid(row=-1, column=0, padx=5, pady=2)
    ttk.Label(columns[0], text="Nickname", background=get_team_color(team1_name.get()), font=('Helvetica', 10, 'bold')).grid(row=-1, column=1, padx=5, pady=2)
    
    ttk.Label(columns[1], text="Player ID", background=get_team_color(team2_name.get()), font=('Helvetica', 10, 'bold')).grid(row=-1, column=2, padx=5, pady=2)
    ttk.Label(columns[1], text="Nickname", background=get_team_color(team2_name.get()), font=('Helvetica', 10, 'bold')).grid(row=-1, column=3, padx=5, pady=2)

    # Player ID and Nickname entry fields
    player_id_entry = ttk.Entry(main_frame)
    player_id_entry.grid(row=4, column=0, padx=10, pady=5)
    nickname_var = tk.StringVar()
    nickname_entry = ttk.Entry(main_frame, textvariable=nickname_var)
    nickname_entry.grid(row=4, column=1, padx=10, pady=5)
    
    ttk.Button(main_frame, text="Submit", command=handle_entry).grid(row=4, column=2, padx=10, pady=5)

    # To move to the next screen (example for the start button)
    def start_game():
        print("Starting game...")
        # You can add logic to switch to the play action screen here

    ttk.Button(main_frame, text="Start Game", command=start_game).grid(row=33, column=3, padx=10, pady=10)

# Main function
def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window during the splash screen

    show_splash_screen(root)  # Show splash screen

    # Database connection
    conn = connect_to_database()
    
    root.after(3100, lambda: [root.deiconify(), player_entry_screen(root, conn)])  # Show player entry screen after splash

    root.title("Laser Tag Player Entry")
    root.geometry("1200x800")  # Initial size of the main window
    root.minsize(600, 400)  # Set a minimum size
    root.maxsize(1920, 1080)  # Set a maximum size (optional)

    # Bind the "q" key to quit the program
    root.bind("q", lambda event: [conn.close(), root.destroy()])

    root.mainloop()

if __name__ == "__main__":
    main()
