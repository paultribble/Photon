import tkinter as tk
import random

# Function to draw background with Tkinter Canvas
def draw_background(canvas):
    canvas.delete("all")  # Clear the canvas
    for _ in range(30):
        start_pos = (random.randint(0, screen_width), random.randint(0, screen_height))
        end_pos = (random.randint(0, screen_width), random.randint(0, screen_height))
        canvas.create_line(start_pos, end_pos, fill="red", width=2)
    canvas.after(100, draw_background, canvas)  # Call draw_background again after 100 ms

# Function for adding a new player
def add_new_player():
    codename = tk.simpledialog.askstring("Input", "Enter New Codename:")
    if codename:
        # Here you can handle database insertion logic if required
        tk.messagebox.showinfo("Success", f"New Player Added: Codename={codename}")

# Create a Tkinter window
screen_width = 1200
screen_height = 800
root = tk.Tk()
root.geometry(f"{screen_width}x{screen_height}")
root.title("Photon Laser Tag Setup")

# Create a canvas to draw on
canvas = tk.Canvas(root, width=screen_width, height=screen_height, bg='black')
canvas.pack()

# Start drawing the background
draw_background(canvas)

# Main Tkinter Frame for input
frame = tk.Frame(root)
frame.pack(pady=10)

# Function to create input form for players
def create_input_form(frame, team_name, color, row):
    team_label = tk.Label(frame, text=team_name, bg=color, font=("Arial", 12, "bold"), width=10)
    team_label.grid(row=row, column=0, padx=10)

    tk.Label(frame, text="ID", font=("Arial", 10, "bold"), width=8).grid(row=row + 1, column=0, padx=5)
    tk.Label(frame, text="Codename", font=("Arial", 10, "bold"), width=10).grid(row=row + 1, column=1, padx=5)

    for i in range(15):
        entry_id = tk.Entry(frame, width=8)
        entry_codename = tk.Entry(frame, width=15)
        entry_id.grid(row=row + 2 + i, column=0, padx=5, pady=2)
        entry_codename.grid(row=row + 2 + i, column=1, padx=5, pady=2)

# Team 1 and Team 2 Entry Forms
create_input_form(frame, "Team 1", "white", 0)
create_input_form(frame, "Team 2", "white", 16)

# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=20)

submit_button = tk.Button(button_frame, text="Submit", width=15, command=add_new_player)
submit_button.grid(row=0, column=0, padx=10)

add_player_button = tk.Button(button_frame, text="Add New Player", command=add_new_player, width=15)
add_player_button.grid(row=0, column=1, padx=10)

# Start the Tkinter main loop
root.mainloop()
