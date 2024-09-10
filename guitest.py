import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import socket
import sys
import os

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

def player_entry_screen(root):
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

    # Bind variables to update function
    team1_name.trace_add("write", lambda *args: update_team_labels())
    team2_name.trace_add("write", lambda *args: update_team_labels())

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

    # Add entries for 15 team members per team
    for i in range(15):
        ttk.Label(main_frame, text=f"Player ID:", background="lightgray").grid(row=2+i, column=0, padx=10, pady=5, sticky="e")
        ttk.Entry(main_frame).grid(row=2+i, column=1, padx=10, pady=5)

        ttk.Label(main_frame, text=f"Nickname:", background="lightgray").grid(row=2+i, column=2, padx=10, pady=5, sticky="e")
        ttk.Entry(main_frame).grid(row=2+i, column=3, padx=10, pady=5)

    for i in range(15):
        ttk.Label(main_frame, text=f"Player ID:", background="lightgray").grid(row=2+i, column=4, padx=10, pady=5, sticky="e")
        ttk.Entry(main_frame).grid(row=2+i, column=5, padx=10, pady=5)

        ttk.Label(main_frame, text=f"Nickname:", background="lightgray").grid(row=2+i, column=6, padx=10, pady=5, sticky="e")
        ttk.Entry(main_frame).grid(row=2+i, column=7, padx=10, pady=5)

    # To move to the next screen (example for the start button)
    def start_game():
        print("Starting game...")
        # You can add logic to switch to the play action screen here

    ttk.Button(main_frame, text="Start Game", command=start_game).grid(row=32, column=3, padx=10, pady=10)

# Main function
def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window during the splash screen

    show_splash_screen(root)  # Show splash screen

    root.after(3100, lambda: [root.deiconify(), player_entry_screen(root)])  # Show player entry screen after splash

    root.title("Laser Tag Player Entry")
    root.geometry("1200x800")  # Initial size of the main window
    root.minsize(600, 400)  # Set a minimum size
    root.maxsize(1920, 1080)  # Set a maximum size (optional)

    # Bind the "q" key to quit the program
    root.bind("q", lambda event: root.destroy())

    root.mainloop()

if __name__ == "__main__":
    main()
