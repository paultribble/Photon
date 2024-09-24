import socket
import threading
import random
import psycopg2
import sys
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk

# Database connection
def connect_to_database():
    try:
        conn = psycopg2.connect(
            dbname="photon",
            user="student",
            # password="student",
            # host="localhost",
            # port="5432"
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL database: {e}")
        sys.exit(1)

# Set up UDP sockets for broadcasting and receiving
def setup_udp_sockets():
    sock_broadcast = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_broadcast.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    sock_receive = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock_receive.bind(('', 7501))
    
    return sock_broadcast, sock_receive

# Splash Screen Function
def show_splash_screen():
    splash = tk.Toplevel()
    splash.title("Welcome to Photon Laser Tag!")
    splash.geometry("400x300")
    splash.configure(bg='black')

    # Load the image
    logo_path = "Images/logo.jpg"  # Path to your image
    logo_image = Image.open(logo_path)  # Open the image
    logo_image = logo_image.resize((300, 200), Image.LANCZOS)  # Resize the image (optional)
    logo_photo = ImageTk.PhotoImage(logo_image)  # Create a PhotoImage object

    label = tk.Label(splash, image=logo_photo, bg='black')
    label.image = logo_photo  # Keep a reference to the image
    label.pack(expand=True)

    # Close splash screen after 3 seconds
    splash.after(3000, splash.destroy)  # 3000 milliseconds = 3 seconds

# Function to broadcast equipment ID
def validate_player_id(player_id_var, codename_entry, equipment_entry, conn, sock_broadcast):
    cursor = conn.cursor()
    player_id = player_id_var.get()
    
    codename_entry.delete(0, tk.END)
    equipment_entry.delete(0, tk.END)
    
    if player_id:  # If ID is not empty
        cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
        result = cursor.fetchone()
        if result:
            codename_entry.insert(0, result[0])  # Insert fetched codename
        else:
            codename_entry.insert(0, "Invalid ID")  # Show "Invalid ID"
    
    equipment_id = equipment_entry.get()
    if equipment_id:
        message = f"Equipment ID {equipment_id} for Player ID {player_id}"
        sock_broadcast.sendto(message.encode(), ('<broadcast>', 7500))  # Broadcast on port 7500
        print(f"Sent: {message}")  # Log the sent message

# Create input forms for team player entries
def create_input_form(frame, team_name, color, row, col, conn, sock_broadcast):
    team_label = tk.Label(frame, text=team_name, bg=color, font=("Arial", 12, "bold"), width=10)
    team_label.grid(row=0, column=col, padx=10)

    tk.Label(frame, text="ID", font=("Arial", 10, "bold"), width=8).grid(row=1, column=col, padx=5)
    tk.Label(frame, text="Codename", font=("Arial", 10, "bold"), width=10).grid(row=1, column=col + 1, padx=5)
    tk.Label(frame, text="Equipment", font=("Arial", 10, "bold"), width=8).grid(row=1, column=col + 2, padx=5)

    entries = []
    for i in range(15):
        player_id_var = tk.StringVar()
        entry_id = tk.Entry(frame, width=8, textvariable=player_id_var)
        entry_codename = tk.Entry(frame, width=15)
        equipment_combobox = ttk.Combobox(frame, width=5, values=list(range(1, 31)))
        equipment_combobox.set("")  # Set default value

        entry_id.grid(row=i + 2, column=col, padx=5, pady=2)
        entry_codename.grid(row=i + 2, column=col + 1, padx=5, pady=2)
        equipment_combobox.grid(row=i + 2, column=col + 2, padx=5, pady=2)

        player_id_var.trace_add("write", lambda name, index, mode, var=player_id_var, codename_entry=entry_codename, equipment_combobox=equipment_combobox: validate_player_id(var, codename_entry, equipment_combobox, conn, sock_broadcast))

        entries.append((entry_id, entry_codename, equipment_combobox))

    return entries

# Function to listen for incoming UDP data
def listen_for_data(sock_receive):
    while True:
        data, addr = sock_receive.recvfrom(1024)  # Receive up to 1024 bytes
        print(f"Received data: {data.decode()} from {addr}")

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

# Function to add a new player through a Tkinter dialog
def add_new_player_tk(conn):
    codename = simpledialog.askstring("Input", "Enter New Codename:")
    if codename:
        cursor = conn.cursor()
        while True:
            new_id = random.randint(1, 99)  # Generate a new ID between 1 and 99
            cursor.execute("SELECT * FROM players WHERE id = %s", (new_id,))
            if cursor.fetchone() is None:
                cursor.execute("INSERT INTO players (id, codename) VALUES (%s, %s)", (new_id, codename))
                conn.commit()
                messagebox.showinfo("Success", f"New Player Added: ID={new_id}, Codename={codename}")
                break

def delete_player(player_id, conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players WHERE id = %s", (player_id,))
    conn.commit()
    messagebox.showinfo("Success", f"Player with ID={player_id} has been deleted.")

# Main Tkinter Frame
root = tk.Tk()
show_splash_screen()  # Show splash screen before main window
root.title("Photon Laser Tag Setup")
root.geometry("1000x800")

# Create a canvas to draw the background
canvas = tk.Canvas(root, width=1000, height=800, bg='black')
canvas.pack()

# Function for generating dynamic background
def draw_background(canvas):
    canvas.delete("all")
    for _ in range(30):
        start_pos = (random.randint(0, 1000), random.randint(0, 800))
        end_pos = (random.randint(0, 1000), random.randint(0, 800))
        canvas.create_line(start_pos, end_pos, fill="red", width=2)
    canvas.after(800, draw_background, canvas)

# Start drawing the background
draw_background(canvas)

# Team Entry Forms
frame = tk.Frame(root, bg='black')
frame.place(relx=0.5, rely=0.3, anchor='center')

conn = connect_to_database()
sock_broadcast, sock_receive = setup_udp_sockets()

receive_thread = threading.Thread(target=listen_for_data, args=(sock_receive,), daemon=True)
receive_thread.start()

team1_entries = create_input_form(frame, "Team 1", "white", 0, 0, conn, sock_broadcast)
team2_entries = create_input_form(frame, "Team 2", "white", 0, 3, conn, sock_broadcast)

# Buttons
button_frame = tk.Frame(root, bg='black')

add_player_button = tk.Button(button_frame, text="Add New Player", command=lambda: add_new_player_tk(conn), width=15)
add_player_button.grid(row=0, column=1, padx=10)

view_database_button = tk.Button(button_frame, text="View Database", command=lambda: show_database_menu_tk(conn), width=15)
view_database_button.grid(row=0, column=2, padx=10)

button_frame.place(relx=0.5, rely=0.6, anchor='center')

# Start Tkinter main loop
root.mainloop()

