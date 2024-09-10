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

    # Main frame
    main_frame = tk.Frame(root, bg="lightgray")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Player ID and Nickname entry fields
    ttk.Label(main_frame, text="Player ID:", background="lightgray").grid(row=0, column=0, padx=10, pady=5, sticky="e")
    player_id_entry = ttk.Entry(main_frame)
    player_id_entry.grid(row=0, column=1, padx=10, pady=5)
    
    ttk.Label(main_frame, text="Nickname:", background="lightgray").grid(row=1, column=0, padx=10, pady=5, sticky="e")
    nickname_var = tk.StringVar()
    nickname_entry = ttk.Entry(main_frame, textvariable=nickname_var)
    nickname_entry.grid(row=1, column=1, padx=10, pady=5)

    ttk.Button(main_frame, text="Submit", command=handle_entry).grid(row=2, column=1, padx=10, pady=5)

    # To move to the next screen (example for the start button)
    def start_game():
        print("Starting game...")
        # You can add logic to switch to the play action screen here

    ttk.Button(main_frame, text="Start Game", command=start_game).grid(row=3, column=1, padx=10, pady=10)

# Main function
def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window during the splash screen

    show_splash_screen(root)  # Show splash screen

    # Database connection
    conn = connect_to_database()

    root.after(3100, lambda: [root.deiconify(), player_entry_screen(root, conn)])  # Show player entry screen after splash

    root.title("Laser Tag Player Entry")
    root.geometry("400x300")  # Adjust size as needed
    root.minsize(300, 200)  # Set a minimum size

    # Bind the "q" key to quit the program
    root.bind("q", lambda event: [conn.close(), root.destroy()])

    root.mainloop()

if __name__ == "__main__":
    main()
