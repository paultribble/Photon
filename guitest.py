import psycopg2
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import socket
import sys
import os
#test
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

# Handle player data
def player_entry_screen(root, conn):
    cursor = conn.cursor()

    # Team variables
    team1_name = tk.StringVar(value="Blue Team")
    team1_color = tk.StringVar(value="blue")
    team2_name = tk.StringVar(value="Red Team")
    team2_color = tk.StringVar(value="red")

    def update_team_names_and_colors(*args):
        # Update Team 1
        team1_label.config(text=team1_name.get(), foreground=team1_color.get())
        # Update Team 2
        team2_label.config(text=team2_name.get(), foreground=team2_color.get())

    # Bind variables to update function
    team1_name.trace_add("write", update_team_names_and_colors)
    team1_color.trace_add("write", update_team_names_and_colors)
    team2_name.trace_add("write", update_team_names_and_colors)
    team2_color.trace_add("write", update_team_names_and_colors)

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

    # Setup the entry form for two teams
    ttk.Label(root, text="Team 1 Name:").grid(row=0, column=0, padx=10, pady=5)
    team1_name_entry = ttk.Entry(root, textvariable=team1_name)
    team1_name_entry.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(root, text="Team 1 Color:").grid(row=1, column=0, padx=10, pady=5)
    team1_color_entry = ttk.Entry(root, textvariable=team1_color)
    team1_color_entry.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(root, text="Team 2 Name:").grid(row=0, column=2, padx=10, pady=5)
    team2_name_entry = ttk.Entry(root, textvariable=team2_name)
    team2_name_entry.grid(row=0, column=3, padx=10, pady=5)

    ttk.Label(root, text="Team 2 Color:").grid(row=1, column=2, padx=10, pady=5)
    team2_color_entry = ttk.Entry(root, textvariable=team2_color)
    team2_color_entry.grid(row=1, column=3, padx=10, pady=5)

    team1_label = ttk.Label(root, text=team1_name.get(), foreground=team1_color.get())
    team1_label.grid(row=2, column=0, columnspan=2, pady=10)
    
    team2_label = ttk.Label(root, text=team2_name.get(), foreground=team2_color.get())
    team2_label.grid(row=2, column=2, columnspan=2, pady=10)

    ttk.Label(root, text="Player ID:").grid(row=4, column=0, padx=10, pady=5)
    player_id_entry = ttk.Entry(root)
    player_id_entry.grid(row=4, column=1, padx=10, pady=5)
    player_id_entry.bind("<Return>", handle_entry)

    nickname_var = tk.StringVar()
    ttk.Label(root, text="Nickname:").grid(row=5, column=0, padx=10, pady=5)
    nickname_entry = ttk.Entry(root, textvariable=nickname_var)
    nickname_entry.grid(row=5, column=1, padx=10, pady=5)
    nickname_entry.bind("<Return>", handle_entry)

    ttk.Button(root, text="Submit", command=handle_entry).grid(row=6, column=1, padx=10, pady=5)

    # To move to the next screen (example for the start button)
    def start_game():
        print("Starting game...")
        # You can add logic to switch to the play action screen here

    ttk.Button(root, text="Start Game", command=start_game).grid(row=7, column=1, padx=10, pady=10)

# Main function
def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window during the splash screen
    
    conn = connect_to_database()
    
    show_splash_screen(root)  # Show splash screen
    
    root.after(3100, lambda: [root.deiconify(), player_entry_screen(root, conn)])  # Show player entry screen after splash

    root.title("Laser Tag Player Entry")
    root.geometry("1200x800")  # Initial size of the main window
    root.minsize(600, 400)  # Set a minimum size
    root.maxsize(1920, 1080)  # Set a maximum size (optional)

    # Bind the "q" key to quit the program
    root.bind("q", lambda event: root.destroy())

    root.mainloop()

if __name__ == "__main__":
    main()