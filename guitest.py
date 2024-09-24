import pygame
import psycopg2
import sys
import random
import tkinter as tk
from tkinter import messagebox, simpledialog

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

# Function to query codename dynamically based on player ID
def query_codename(entry_id, entry_codename, conn):
    player_id = entry_id.get()
    if player_id.isdigit():  # Check if player_id is a number
        cursor = conn.cursor()
        cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
        result = cursor.fetchone()
        if result:
            entry_codename.delete(0, tk.END)
            entry_codename.insert(0, result[0])  # Insert fetched codename
        else:
            entry_codename.delete(0, tk.END)
            entry_codename.insert(0, "Invalid ID")
    else:
        entry_codename.delete(0, tk.END)
        entry_codename.insert(0, "Invalid ID")

# Function to create input forms with dynamic codename check
def create_input_form(frame, team_name, color, row, col, conn):
    team_label = tk.Label(frame, text=team_name, bg=color, font=("Arial", 12, "bold"), width=10)
    team_label.grid(row=0, column=col, padx=10)

    tk.Label(frame, text="ID", font=("Arial", 10, "bold"), width=8).grid(row=1, column=col, padx=5)
    tk.Label(frame, text="Codename", font=("Arial", 10, "bold"), width=10).grid(row=1, column=col + 1, padx=5)
    tk.Label(frame, text="Equip ID", font=("Arial", 10, "bold"), width=8).grid(row=1, column=col + 2, padx=5)

    entries = []
    for i in range(15):
        entry_id = tk.Entry(frame, width=8)
        entry_codename = tk.Entry(frame, width=15)
        entry_equip_id = tk.Entry(frame, width=5)

        entry_id.grid(row=i + 2, column=col, padx=5, pady=2)
        entry_codename.grid(row=i + 2, column=col + 1, padx=5, pady=2)
        entry_equip_id.grid(row=i + 2, column=col + 2, padx=5, pady=2)

        # Use Tkinter's trace to dynamically check for codename as user types
        entry_id_var = tk.StringVar()
        entry_id.config(textvariable=entry_id_var)
        entry_id_var.trace_add("write", lambda name, index, mode, var=entry_id_var, eid=entry_id, ecodename=entry_codename: query_codename(eid, ecodename, conn))

        entries.append((entry_id, entry_codename, entry_equip_id))
    
    return entries

# Adding new player through Tkinter
def add_new_player_tk(conn):
    codename = simpledialog.askstring("Input", "Enter New Codename:")
    if codename:
        cursor = conn.cursor()
        while True:
            new_id = random.randint(1, 99)
            cursor.execute("SELECT * FROM players WHERE id = %s", (new_id,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO players (id, codename) VALUES (%s, %s)", (new_id, codename))
                conn.commit()
                messagebox.showinfo("Success", f"New Player Added: ID={new_id}, Codename={codename}")
                break

# Function to clear the database
def clear_database(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players")
    conn.commit()
    print("Database cleared.")

# View database function
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

# Function for generating dynamic background
def draw_background(canvas):
    canvas.delete("all")
    for _ in range(30):
        start_pos = (random.randint(0, 1000), random.randint(0, 800))
        end_pos = (random.randint(0, 1000), random.randint(0, 800))
        canvas.create_line(start_pos, end_pos, fill="red", width=2)
    canvas.after(800, draw_background, canvas)

# Main Tkinter Frame
root = tk.Tk()
root.title("Photon Laser Tag Setup")
root.geometry("1000x800")

# Create a canvas to draw the background
canvas = tk.Canvas(root, width=1000, height=800, bg='black')
canvas.pack()

# Start drawing the background
draw_background(canvas)

# Team Entry Forms
frame = tk.Frame(root, bg='black')
frame.place(relx=0.5, rely=0.3, anchor='center')  # Center the frame
team1_entries = create_input_form(frame, "Team 1", "white", 0, 0, connect_to_database())
team2_entries = create_input_form(frame, "Team 2", "white", 0, 3, connect_to_database())  # Adjusted column for right-side

# Buttons Frame
button_frame = tk.Frame(root, bg='black')

# Submit Button: For any remaining form submission tasks
submit_button = tk.Button(button_frame, text="Submit", width=15)
submit_button.grid(row=0, column=0, padx=10)

# Add new player button
add_player_button = tk.Button(button_frame, text="Add New Player", command=lambda: add_new_player_tk(connect_to_database()), width=15)
add_player_button.grid(row=0, column=1, padx=10)

# View database button
view_database_button = tk.Button(button_frame, text="View Database", command=lambda: show_database_menu_tk(connect_to_database()), width=15)
view_database_button.grid(row=0, column=2, padx=10)

# Position the button frame
button_frame.place(relx=0.5, rely=0.6, anchor='center')

# Start Tkinter main loop
root.mainloop()
