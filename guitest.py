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

# Function to fetch and validate codename for the entered ID
def validate_player_id(player_id_var, codename_entry, equipment_entry, conn):
    cursor = conn.cursor()
    player_id = player_id_var.get()
    
    # Clear codename and equipment fields
    codename_entry.delete(0, tk.END)
    equipment_entry.delete(0, tk.END)
    
    if player_id:  # If ID is not empty
        cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
        result = cursor.fetchone()
        if result:
            codename_entry.insert(0, result[0])  # Insert fetched codename
        else:
            codename_entry.insert(0, "Invalid ID")  # Show "Invalid ID"
    else:
        codename_entry.delete(0, tk.END)  # Clear "Invalid ID" if field is empty

# Function for creating input forms
def create_input_form(frame, team_name, color, row, col, conn):
    team_label = tk.Label(frame, text=team_name, bg=color, font=("Arial", 12, "bold"), width=10)
    team_label.grid(row=0, column=col, padx=10)

    tk.Label(frame, text="ID", font=("Arial", 10, "bold"), width=8).grid(row=1, column=col, padx=5)
    tk.Label(frame, text="Codename", font=("Arial", 10, "bold"), width=10).grid(row=1, column=col + 1, padx=5)
    tk.Label(frame, text="Equipment", font=("Arial", 10, "bold"), width=8).grid(row=1, column=col + 2, padx=5)

    entries = []
    for i in range(15):
        # Create StringVar to track player ID changes
        player_id_var = tk.StringVar()

        entry_id = tk.Entry(frame, width=8, textvariable=player_id_var)
        entry_codename = tk.Entry(frame, width=15)
        entry_equipment = tk.Entry(frame, width=5)  # Small input for Equipment ID
        
        entry_id.grid(row=i + 2, column=col, padx=5, pady=2)
        entry_codename.grid(row=i + 2, column=col + 1, padx=5, pady=2)
        entry_equipment.grid(row=i + 2, column=col + 2, padx=5, pady=2)

        # Bind the StringVar to the validate function dynamically
        player_id_var.trace_add("write", lambda name, index, mode, var=player_id_var, codename_entry=entry_codename, equipment_entry=entry_equipment: validate_player_id(var, codename_entry, equipment_entry, conn))

        entries.append((entry_id, entry_codename, entry_equipment))

    return entries

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




# Main Tkinter Frame
root = tk.Tk()
root.title("Photon Laser Tag Setup")
root.geometry("1000x800")

# Create a canvas to draw the background
canvas = tk.Canvas(root, width=1000, height=800, bg='black')
canvas.pack()

# Function for generating dynamic background
def draw_background(canvas):
    canvas.delete("all")  # Clear the canvas
    for _ in range(30):
        start_pos = (random.randint(0, 1000), random.randint(0, 800))
        end_pos = (random.randint(0, 1000), random.randint(0, 800))
        canvas.create_line(start_pos, end_pos, fill="red", width=2)
    canvas.after(800, draw_background, canvas)  # Call draw_background again after 100 ms

# Start drawing the background
draw_background(canvas)

# Team Entry Forms
frame = tk.Frame(root, bg='black')
frame.place(relx=0.5, rely=0.3, anchor='center')  # Center the frame

conn = connect_to_database()

team1_entries = create_input_form(frame, "Team 1", "white", 0, 0, conn)
team2_entries = create_input_form(frame, "Team 2", "white", 0, 3, conn)  # Adjust for the second team

# Buttons
button_frame = tk.Frame(root, bg='black')

# Submit Button: No longer needed since dynamic checking is used.
add_player_button = tk.Button(button_frame, text="Add New Player", command=lambda: add_new_player_tk(conn), width=15)
add_player_button.grid(row=0, column=1, padx=10)

# View database
view_database_button = tk.Button(button_frame, text="View Database", command=lambda: show_database_menu_tk(conn), width=15)
view_database_button.grid(row=0, column=2, padx=10)

# Position the button frame right under the player entry frame
button_frame.place(relx=0.5, rely=0.6, anchor='center')  # Adjust 'rely' to control vertical placement

# Start Tkinter main loop
root.mainloop()