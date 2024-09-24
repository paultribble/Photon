import pygame
import psycopg2
import sys
import random
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog

# Pygame initialization
pygame.init()

# Window Dimensions
screen_width = 1200
screen_height = 800
pygame.display.set_caption("Photon Laser Tag")

# Database connection
def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname="photon",
            user="student",
            password="student",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        sys.exit(1)

# Tkinter Window setup
root = tk.Tk()
root.title("Photon Laser Tag Setup")
root.geometry("1200x800")

# Colors for team selection
dropdown_colors = {
    "White": "#FFFFFF", "Black": "#000000", "Blue": "#0000FF",
    "Red": "#FF0000", "Green": "#00FF00", "Yellow": "#FFFF00",
    "Orange": "#FFA500", "Pink": "#FFC0CB", "Navy": "#000080"
}

# Create the main Pygame display for laser background animation
screen = pygame.display.set_mode((screen_width, screen_height))

# Function for generating laser lines
def draw_lasers():
    screen.fill((0, 0, 0))
    for _ in range(30):
        start_pos = (random.randint(0, screen_width), random.randint(0, screen_height))
        end_pos = (random.randint(0, screen_width), random.randint(0, screen_height))
        pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 2)
    pygame.display.flip()

# Background gradient drawing function
def draw_gradient_background():
    for y in range(screen_height):
        for x in range(screen_width):
            color = (x // 5, y // 5, (x + y) // 10)
            screen.set_at((x, y), color)
    draw_lasers()

# Function for Tkinter input form generation
def create_input_form(frame, team_name, color, row, col):
    team_label = tk.Label(frame, text=team_name, bg=color, font=("Arial", 12, "bold"), width=10)
    team_label.grid(row=0, column=col, padx=10)

    tk.Label(frame, text="ID", font=("Arial", 10, "bold"), width=8).grid(row=1, column=col, padx=5)
    tk.Label(frame, text="Codename", font=("Arial", 10, "bold"), width=10).grid(row=1, column=col+1, padx=5)

    for i in range(15):
        entry_id = tk.Entry(frame, width=8)
        entry_codename = tk.Entry(frame, width=15)
        entry_id.grid(row=i+2, column=col, padx=5, pady=2)
        entry_codename.grid(row=i+2, column=col+1, padx=5, pady=2)

# Function to clear database
def clear_database(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players")
    conn.commit()
    print("Database cleared.")

# Adding new player through Tkinter
def add_new_player_tk(conn):
    codename = simpledialog.askstring("Input", "Enter New Codename:")
    if codename:
        cursor = conn.cursor()
        while True:
            new_id = random.randint(1, 999999)
            cursor.execute("SELECT * FROM players WHERE id = %s", (new_id,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO players (id, codename) VALUES (%s, %s)", (new_id, codename))
                conn.commit()
                messagebox.showinfo("Success", f"New Player Added: ID={new_id}, Codename={codename}")
                break

# View database
def show_database_menu_tk(conn):
    cursor = conn.cursor()
    cursor.execute("SELECT id, codename FROM players ORDER BY codename ASC")
    entries = cursor.fetchall()

    database_window = tk.Toplevel(root)
    database_window.title("Player Database")

    for i, (player_id, codename) in enumerate(entries):
        tk.Label(database_window, text=f"{player_id}: {codename}").grid(row=i, column=0)
        tk.Button(database_window, text="Delete", command=lambda pid=player_id: delete_player(pid, conn)).grid(row=i, column=1)

def delete_player(player_id, conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE id = %s", (player_id,))
    conn.commit()
    messagebox.showinfo("Success", f"Player with ID={player_id} has been deleted.")

# Main Tkinter Frame
frame = tk.Frame(root)
frame.pack(pady=10)

# Team 1 and Team 2 Entry Forms
create_input_form(frame, "Team 1", "white", 0, 0)
create_input_form(frame, "Team 2", "white", 0, 2)

# Submit and Other Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

submit_button = tk.Button(button_frame, text="Submit", width=15)
submit_button.grid(row=0, column=0, padx=10)

add_player_button = tk.Button(button_frame, text="Add New Player", command=lambda: add_new_player_tk(conn), width=15)
add_player_button.grid(row=0, column=1, padx=10)

view_database_button = tk.Button(button_frame, text="View Database", command=lambda: show_database_menu_tk(conn), width=15)
view_database_button.grid(row=0, column=2, padx=10)

# Run the Pygame laser background animation in a separate thread
def run_pygame_background():
    clock = pygame.time.Clock()
    while True:
        draw_gradient_background()
        clock.tick(60)

# Run Pygame in a new thread
import threading
pygame_thread = threading.Thread(target=run_pygame_background)
pygame_thread.daemon = True
pygame_thread.start()

# Database connection
conn = connect_to_database()

# Tkinter main loop
root.mainloop()

