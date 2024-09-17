import pygame
import psycopg2
import sys
import random
import os
import math
import tkinter as tk
from tkinter import simpledialog

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Photon Laser Tag")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)
blue = (0, 0, 255)
red = (255, 0, 0)
green = (0, 255, 0)
yellow = (255, 255, 0)
orange = (255, 165, 0)
pink = (255, 0, 255)
navy = (0, 0, 128)

# Dropdown menu colors
dropdown_colors = {
    "White": white,
    "Black": black,
    "Blue": blue,
    "Red": red,
    "Green": green,
    "Yellow": yellow,
    "Orange": orange,
    "Pink": pink,
    "Navy": navy
}

# Fonts
font = pygame.font.Font(None, 36)

def calculate_brightness(color):
    r, g, b = color
    return (0.299 * r + 0.587 * g + 0.114 * b)

# Function to get contrasting text color
def get_contrasting_color(background_color):
    brightness = calculate_brightness(background_color)
    return (255, 255, 255) if brightness < 128 else (0, 0, 0)  # White text if dark, Black text if bright

class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = gray
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.txt_surface = self.font.render(text, True, black)
        self.callback = callback

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.callback()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + (self.rect.w - self.txt_surface.get_width()) // 2,
                                       self.rect.y + (self.rect.h - self.txt_surface.get_height()) // 2))

# Load logo image
def load_image(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "Images", filename)
    return pygame.image.load(image_path)

# Resize image to fit modestly in the center of the screen
def resize_image(image, max_width, max_height):
    img_width, img_height = image.get_size()
    width_ratio = max_width / img_width
    height_ratio = max_height / img_height
    min_ratio = min(width_ratio, height_ratio)
    new_width = int(img_width * min_ratio)
    new_height = int(img_height * min_ratio)
    return pygame.transform.scale(image, (new_width, new_height))

# Database connection function
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

class TextBox:
    def __init__(self, x, y, w, h, text='', readonly=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = pygame.Color('lightskyblue3')
        self.text = text
        self.txt_surface = font.render(text, True, black)
        self.active = False
        self.readonly = readonly

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = pygame.Color('dodgerblue2') if self.active else pygame.Color('lightskyblue3')

        if event.type == pygame.KEYDOWN and not self.readonly:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = font.render(self.text, True, black)

    def draw(self, screen, border_color=None):
        border_color = border_color if border_color is not None else black
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, border_color, self.rect, 2)

# Dropdown menu class
class DropdownMenu:
    def __init__(self, x, y, w, h, options):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = gray
        self.options = options
        self.selected_option = list(options.keys())[0]
        self.font = pygame.font.Font(None, 36)
        self.txt_surface = self.font.render(self.selected_option, True, black)
        self.dropdown_open = False
        self.option_rects = []

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.dropdown_open = not self.dropdown_open
                if self.dropdown_open:
                    self.option_rects = [pygame.Rect(self.rect.x, self.rect.y + (i + 1) * 40, self.rect.w, 40) for i in range(len(self.options))]
            elif self.dropdown_open:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_option = list(self.options.keys())[i]
                        self.txt_surface = self.font.render(self.selected_option, True, black)
                        self.dropdown_open = False
                        break

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        if self.dropdown_open:
            for i, rect in enumerate(self.option_rects):
                pygame.draw.rect(screen, gray, rect)
                screen.blit(self.font.render(list(self.options.keys())[i], True, black), (rect.x + 5, rect.y + 5))

class DatabaseMenu:
    def __init__(self, x, y, w, h, conn):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = gray
        self.scroll_y = 0
        self.conn = conn
        self.entries = []
        self.fetch_entries()

    def fetch_entries(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, codename FROM players ORDER BY codename ASC")
        self.entries = cursor.fetchall()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            print(f"Mouse clicked at: {event.pos}")  # Debugging line

            if event.button == 4:  # Scroll up
                self.scroll_y = max(self.scroll_y - 10, 0)
                print("Scrolled up")  # Debugging line
            elif event.button == 5:  # Scroll down
                self.scroll_y = min(self.scroll_y + 10, max(0, len(self.entries) * 40 - self.rect.height))
                print("Scrolled down")  # Debugging line

            for i, entry_rect in enumerate(self.entry_rects):
                if entry_rect.collidepoint(event.pos):
                    print(f"Clicked within entry rect: {i}")  # Debugging line
                    if self.remove_buttons[i].collidepoint(event.pos):
                        print(f"Clicked on 'X' button for entry: {self.entries[i][0]}")  # Debugging line
                        self.remove_entry(self.entries[i][0])
                        self.fetch_entries()  # Refresh entries after removal
                    break

    def remove_entry(self, entry_id):
        print(f"Attempting to remove entry with ID: {entry_id}")  # Debugging line
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM players WHERE id = %s", (entry_id,))
        self.conn.commit()
        print(f"Entry with ID: {entry_id} removed")  # Debugging line

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        cursor_y = self.rect.y - self.scroll_y
        self.entry_rects = []
        self.remove_buttons = []
        for i, (player_id, codename) in enumerate(self.entries):
            entry_rect = pygame.Rect(self.rect.x, cursor_y + i * 40, self.rect.w - 40, 40)
            remove_button = pygame.Rect(self.rect.x + self.rect.w - 40, cursor_y + i * 40, 40, 40)
            self.entry_rects.append(entry_rect)
            self.remove_buttons.append(remove_button)
            pygame.draw.rect(screen, white, entry_rect)
            pygame.draw.rect(screen, black, remove_button)
            screen.blit(font.render(f"{player_id} - {codename}", True, black), (entry_rect.x + 5, entry_rect.y + 5))
            screen.blit(font.render('X', True, white), (remove_button.x + 10, remove_button.y + 5))

def show_add_player_form():
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    player_name = simpledialog.askstring("New Player", "Enter Player Codename:")
    root.destroy()
    return player_name

def main():
    clock = pygame.time.Clock()
    running = True
    conn = connect_to_database()

    # Initialize dropdown menu
    dropdown_menu = DropdownMenu(50, 50, 200, 40, dropdown_colors)
    
    # Initialize database menu
    database_menu = DatabaseMenu(400, 50, 400, 700, conn)
    
    # Initialize buttons
    add_player_button = Button(50, 150, 200, 50, 'Add New Player', lambda: show_add_player_form())

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            dropdown_menu.handle_event(event)
            database_menu.handle_event(event)
            add_player_button.handle_event(event)

        # Clear screen
        screen.fill(black)
        
        # Draw dropdown menu
        dropdown_menu.draw(screen)
        
        # Draw database menu
        database_menu.draw(screen)
        
        # Draw buttons
        add_player_button.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()
    conn.close()

if __name__ == "__main__":
    main()
