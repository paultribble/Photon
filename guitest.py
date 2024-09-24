import tkinter as tk
import pygame
import os
import threading
from time import sleep

# Pygame background drawing
screen_width = 800
screen_height = 600

def draw_gradient_background():
    screen.fill((0, 0, 0))  # Fill background with black

    for i in range(screen_height):
        color = (i % 255, i % 255, 255)  # Dynamic gradient effect
        pygame.draw.line(screen, color, (0, i), (screen_width, i))

    # Drawing random neon red lines (lasers)
    import random
    for _ in range(30):
        start_pos = (random.randint(0, screen_width), random.randint(0, screen_height))
        end_pos = (random.randint(0, screen_width), random.randint(0, screen_height))
        pygame.draw.line(screen, (255, 0, 0), start_pos, end_pos, 2)

def run_pygame_background():
    global screen
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Photon Laser Tag Background")

    running = True
    while running:
        draw_gradient_background()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.time.delay(30)  # Adjust speed of background updates

    pygame.quit()

# Tkinter Splash Screen
def show_splash_screen(root):
    splash = tk.Toplevel(root)
    splash.title("Photon Laser Tag")
    splash.geometry("400x300")

    label = tk.Label(splash, text="Welcome to Photon Laser Tag!", font=("Arial", 24))
    label.pack(pady=50)

    splash.after(3000, splash.destroy)  # Show splash screen for 3 seconds

# Tkinter Player Entry Screen
def show_player_entry_screen(root):
    entry_screen = tk.Toplevel(root)
    entry_screen.title("Player Entry")
    entry_screen.geometry("800x600")

    # Team 1
    team1_label = tk.Label(entry_screen, text="Team 1", font=("Arial", 18))
    team1_label.grid(row=0, column=0, columnspan=2, padx=10, pady=10)

    for i in range(15):
        tk.Entry(entry_screen, width=10).grid(row=i+1, column=0, padx=5, pady=5)
        tk.Entry(entry_screen, width=10).grid(row=i+1, column=1, padx=5, pady=5)

    # Team 2
    team2_label = tk.Label(entry_screen, text="Team 2", font=("Arial", 18))
    team2_label.grid(row=0, column=2, columnspan=2, padx=10, pady=10)

    for i in range(15):
        tk.Entry(entry_screen, width=10).grid(row=i+1, column=2, padx=5, pady=5)
        tk.Entry(entry_screen, width=10).grid(row=i+1, column=3, padx=5, pady=5)

    # Buttons
    submit_button = tk.Button(entry_screen, text="Submit", width=15)
    submit_button.grid(row=16, column=0, columnspan=2, pady=20)

    add_player_button = tk.Button(entry_screen, text="Add New Player", width=15)
    add_player_button.grid(row=16, column=2, columnspan=2, pady=20)

    view_db_button = tk.Button(entry_screen, text="View Database", width=15)
    view_db_button.grid(row=17, column=1, columnspan=2, pady=20)

# Main Tkinter loop
def run_tkinter_app():
    root = tk.Tk()
    root.title("Photon Laser Tag Main")
    root.geometry("800x600")

    # Show splash screen and then player entry screen after
    show_splash_screen(root)
    root.after(3000, lambda: show_player_entry_screen(root))  # Delay player entry screen by 3 seconds

    root.mainloop()

# Start the Pygame background in a separate thread
pygame_thread = threading.Thread(target=run_pygame_background)
pygame_thread.daemon = True
pygame_thread.start()

# Start the Tkinter app
run_tkinter_app()




