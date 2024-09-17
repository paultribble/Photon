import psycopg2
import sys
import random
import os
import pygame

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
            # If the user clicked on the input box rect.
            if self.rect.collidepoint(event.pos):
                # Toggle the active variable.
                self.active = not self.active
            else:
                self.active = False
            # Change the current color of the input box.
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
                # Re-render the text.
                self.txt_surface = font.render(self.text, True, black)

    def draw(self, screen, border_color=None):
        # Use the provided border_color or default to black if not provided
        border_color = border_color if border_color is not None else black

        # Draw the text.
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Draw the rect.
        pygame.draw.rect(screen, border_color, self.rect, 2)  # The '2' means the border thickness.

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

        # Define the up and down arrow buttons
        self.scroll_up_button = Button(x + w + 10, y + 10, 40, 30, "Up", self.scroll_up)
        self.scroll_down_button = Button(x + w + 10, y + h - 40, 60, 30, "Down", self.scroll_down)

    def fetch_entries(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, codename FROM players ORDER BY codename ASC")
        self.entries = cursor.fetchall()

    def scroll_up(self):
        self.scroll_y = max(self.scroll_y - 5 * 40, 0)

    def scroll_down(self):
        self.scroll_y = min(self.scroll_y + 5 * 40, max(0, len(self.entries) * 40 - self.rect.height))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if self.scroll_up_button.rect.collidepoint(event.pos):
                    self.scroll_up()
                elif self.scroll_down_button.rect.collidepoint(event.pos):
                    self.scroll_down()

            for i, entry_rect in enumerate(self.entry_rects):
                if entry_rect.collidepoint(event.pos):
                    if self.remove_buttons[i].collidepoint(event.pos):
                        self.remove_entry(self.entries[i][0])
                        self.fetch_entries()  # Refresh entries after removal
                    break

    def remove_entry(self, entry_id):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM players WHERE id = %s", (entry_id,))
        self.conn.commit()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        cursor_y = self.rect.y - self.scroll_y
        self.entry_rects = []
        self.remove_buttons = []

        for i, (entry_id, codename) in enumerate(self.entries):
            entry_rect = pygame.Rect(self.rect.x + 10, cursor_y + i * 40, self.rect.w - 20, 40)
            self.entry_rects.append(entry_rect)

            pygame.draw.rect(screen, gray, entry_rect)
            screen.blit(font.render(f"ID: {entry_id} - Codename: {codename}", True, black), (entry_rect.x + 5, entry_rect.y + 5))

            remove_button_rect = pygame.Rect(entry_rect.x + entry_rect.w - 30, entry_rect.y + 5, 20, 20)
            pygame.draw.rect(screen, red, remove_button_rect)
            screen.blit(font.render("X", True, black), (remove_button_rect.x + 5, remove_button_rect.y + 2))
            self.remove_buttons.append(remove_button_rect)

        self.scroll_up_button.draw(screen)
        self.scroll_down_button.draw(screen)

class MainMenu:
    def __init__(self):
        self.splash_screen()

    def splash_screen(self):
        # Load and resize logo
        logo = load_image("logo.png")
        logo = resize_image(logo, 200, 100)
        logo_x = (screen_width - logo.get_width()) // 2
        logo_y = (screen_height - logo.get_height()) // 2
        logo_rect = pygame.Rect(logo_x, logo_y, logo.get_width(), logo.get_height())

        # Create buttons
        start_button = Button(screen_width // 2 - 50, screen_height // 2 + 60, 100, 50, "Start", self.start_game)
        quit_button = Button(screen_width // 2 - 50, screen_height // 2 + 120, 100, 50, "Quit", pygame.quit)

        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                start_button.handle_event(event)
                quit_button.handle_event(event)

            screen.fill(black)
            screen.blit(logo, logo_rect.topleft)
            start_button.draw(screen)
            quit_button.draw(screen)
            pygame.display.flip()
            clock.tick(30)

    def start_game(self):
        player_entry_screen()

def player_entry_screen():
    conn = connect_to_database()
    blue_team_color = dropdown_colors["Blue"]
    red_team_color = dropdown_colors["Red"]

    blue_team_dropdown = DropdownMenu(50, 50, 200, 40, dropdown_colors)
    red_team_dropdown = DropdownMenu(50, 100, 200, 40, dropdown_colors)

    blue_team_textbox = TextBox(50, 150, 200, 40)
    red_team_textbox = TextBox(50, 200, 200, 40)

    submit_button = Button(screen_width // 2 - 50, screen_height - 100, 100, 50, "Submit", lambda: print("Submit pressed"))

    database_menu = DatabaseMenu(50, 300, screen_width - 100, screen_height - 400, conn)

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            blue_team_dropdown.handle_event(event)
            red_team_dropdown.handle_event(event)
            blue_team_textbox.handle_event(event)
            red_team_textbox.handle_event(event)
            submit_button.handle_event(event)
            database_menu.handle_event(event)

        screen.fill(black)

        # Draw dropdowns
        blue_team_dropdown.draw(screen)
        red_team_dropdown.draw(screen)

        # Draw textboxes
        blue_team_textbox.draw(screen)
        red_team_textbox.draw(screen)

        # Draw submit button
        submit_button.draw(screen)

        # Draw database menu
        database_menu.draw(screen)

        pygame.display.flip()
        clock.tick(30)

if __name__ == "__main__":
    MainMenu()
