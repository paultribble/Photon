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

# Function to start the main window after splash
def start_main_window():
    root.deiconify()  # Show the main window after the splash screen

# Function to update codename field dynamically based on typed ID
def update_codename(player_id_var, codename_entry, conn):
    player_id = player_id_var.get()

    # Clear the codename entry field before updating
    codename_entry.delete(0, tk.END)

    if player_id.isdigit():  # Check if the input is numeric
        cursor = conn.cursor()
        cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
        result = cursor.fetchone()

        if result:
            codename_entry.insert(0, result[0])  # Insert codename
            codename_entry.config(fg='black')    # Reset color to black
        else:
            codename_entry.insert(0, "Invalid ID")
            codename_entry.config(fg='gray')  # Set text color to gray
    else:
        codename_entry.config(fg='black')  # Reset color to black for non-numeric input

# Modified validate_and_broadcast to reset the color once Enter is pressed
def validate_and_broadcast(player_id_var, codename_entry, equipment_entry, conn, sock_broadcast):
    cursor = conn.cursor()
    player_id = player_id_var.get()
    equipment_id = equipment_entry.get()

    # Temporary variable for equipment ID and player details
    temporary_data = {}

    if player_id:  # If ID is not empty
        cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
        result = cursor.fetchone()
        if result:
            codename_entry.delete(0, tk.END)
            codename_entry.insert(0, result[0])  # Insert fetched codename
            codename_entry.config(fg='black')    # Reset color to black once validated
            temporary_data[player_id] = {'codename': result[0], 'equipment_id': equipment_id}  # Store player data
        else:
            codename_entry.delete(0, tk.END)
            codename_entry.insert(0, "Invalid ID")
            codename_entry.config(fg='gray')  # Keep text gray if ID is invalid
            return

    if equipment_id:
        message = f"Equipment ID: {equipment_id}"  # Send only the Equipment ID
        sock_broadcast.sendto(message.encode(), ('<broadcast>', 7500))  # Broadcast on port 7500
        print(f"Sent: {message}")  # Log the sent message
    else:
        messagebox.showwarning("Warning", "Equipment ID cannot be empty.")

# In create_input_form, bind the update_codename function to the player ID entry
def create_input_form(frame, team_name, color, row, col, conn, sock_broadcast):
    team_label = tk.Label(frame, text=team_name, bg=color, font=("Arial", 12, "bold"), width=10)
    team_label.grid(row=0, column=col, padx=10)

    tk.Label(frame, text="ID", font=("Arial", 10, "bold"), width=8).grid(row=1, column=col, padx=5)
    tk.Label(frame, text="Codename", font=("Arial", 10, "bold"), width=10).grid(row=1, column=col + 1, padx=5)
    tk.Label(frame, text="Equipment", font=("Arial", 10, "bold"), width=10).grid(row=1, column=col + 2, padx=5)

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

        # Bind the update_codename function to player ID field updates
        player_id_var.trace_add('write', lambda name, index, mode, pid_var=player_id_var, codename=entry_codename: update_codename(pid_var, codename, conn))

        # Add enter button to validate and broadcast
        enter_button = tk.Button(frame, text="Enter", command=lambda pid_var=player_id_var, codename=entry_codename, equip=equipment_combobox: validate_and_broadcast(pid_var, codename, equip, conn, sock_broadcast))
        enter_button.grid(row=i + 2, column=col + 3, padx=5, pady=2)

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
root.withdraw()  # Hide the main window initially

# Show the splash screen and run the main window after it
show_splash_screen()
root.after(3000, start_main_window)

# Set up sockets and database connection
sock_broadcast, sock_receive = setup_udp_sockets()
conn = connect_to_database()

# Start the UDP listener in a separate thread
listener_thread = threading.Thread(target=listen_for_data, args=(sock_receive,), daemon=True)
listener_thread.start()

# Create the input form for players
frame = tk.Frame(root)
frame.pack(pady=20)
create_input_form(frame, "Blue Team", "blue", 0, 0, conn, sock_broadcast)
create_input_form(frame, "Red Team", "red", 0, 4, conn, sock_broadcast)

# Create menu for database operations
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)
database_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Database", menu=database_menu)
database_menu.add_command(label="Show Players", command=lambda: show_database_menu_tk(conn))
database_menu.add_command(label="Add Player", command=lambda: add_new_player_tk(conn))
database_menu.add_command(label="Clear Database", command=lambda: clear_database(conn))

# Run the main event loop
root.mainloop()

# Cleanup on exit
sock_broadcast.close()
sock_receive.close()
conn.close()
