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

<<<<<<< HEAD
# Database connection
=======
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


def clear_database(conn):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM players")
    conn.commit()
    print("Database cleared.")

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
>>>>>>> ed3f4e1a6fa634f57d892939faef75d57cfbcc0e
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

<<<<<<< HEAD
# Tkinter Window setup
root = tk.Tk()
root.title("Photon Laser Tag Setup")
root.geometry("1200x800")
=======
# Text input box class for pygame window
class TextBox:
    def __init__(self, x, y, w, h, text='', readonly=False):
        # Initialize the text box with the provided dimensions
        self.rect = pygame.Rect(x, y, w, h)
        # Initialize the text box with the provided color
        self.color = pygame.Color('lightskyblue3')
        self.text = text
        self.txt_surface = font.render(text, True, black)
        # Initialize the text box as inactive
        self.active = False
        self.readonly = readonly
>>>>>>> ed3f4e1a6fa634f57d892939faef75d57cfbcc0e

# Colors for team selection
dropdown_colors = {
    "White": "#FFFFFF", "Black": "#000000", "Blue": "#0000FF",
    "Red": "#FF0000", "Green": "#00FF00", "Yellow": "#FFFF00",
    "Orange": "#FFA500", "Pink": "#FFC0CB", "Navy": "#000080"
}

# Create the main Pygame display for laser background animation
screen = pygame.display.set_mode((screen_width, screen_height))

<<<<<<< HEAD
# Function for generating laser lines
def draw_lasers():
    screen.fill((0, 0, 0))
=======
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

# Database menu class
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

        for i, (player_id, codename) in enumerate(self.entries):
            entry_rect = pygame.Rect(self.rect.x, cursor_y + i * 40, self.rect.width - 50, 40)
            pygame.draw.rect(screen, white, entry_rect)
            pygame.draw.rect(screen, black, entry_rect, 2)
            text_surface = font.render(f"{player_id}: {codename}", True, black)
            screen.blit(text_surface, (entry_rect.x + 5, entry_rect.y + 5))

            remove_button_rect = pygame.Rect(entry_rect.right, cursor_y + i * 40, 50, 40)
            pygame.draw.rect(screen, red, remove_button_rect)
            pygame.draw.rect(screen, black, remove_button_rect, 2)
            remove_text_surface = font.render("X", True, black)
            screen.blit(remove_text_surface, (remove_button_rect.x + (remove_button_rect.w - remove_text_surface.get_width()) // 2,
                                              remove_button_rect.y + (remove_button_rect.h - remove_text_surface.get_height()) // 2))
            self.entry_rects.append(entry_rect)
            self.remove_buttons.append(remove_button_rect)

        # Draw the scroll buttons
        self.scroll_up_button.draw(screen)
        self.scroll_down_button.draw(screen)

def show_database_menu(conn):
    modal_running = True
    db_menu = DatabaseMenu(100, 100, 1000, 600, conn)
    clock = pygame.time.Clock()

    def close_modal():
        nonlocal modal_running
        modal_running = False

    close_button = Button(1050, 50, 50, 30, "X", close_modal)

    while modal_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            db_menu.handle_event(event)
            close_button.handle_event(event)

        screen.fill(black)
        draw_gradient_background(screen)
        draw_neon_lines(screen)

        db_menu.draw(screen)
        close_button.draw(screen)

        pygame.display.flip()
        clock.tick(80)



# Fetch codename from database based on ID
def fetch_codename_from_db(player_id, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return ""

def add_new_player(conn, codename):
    cursor = conn.cursor()
    while True:
        new_id = random.randint(1, 999999)
        cursor.execute("SELECT * FROM players WHERE id = %s", (new_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO players (id, codename) VALUES (%s, %s)", (new_id, codename))
            conn.commit()
            return new_id

def show_new_player_menu(conn):
    modal_running = True
    new_codename_box = TextBox(450, 300, 300, 40)
    clock = pygame.time.Clock()

    result_id = ""
    result_codename = ""

    def save_new_player():
        nonlocal result_id, result_codename
        codename = new_codename_box.text
        if codename:
            new_id = add_new_player(conn, codename)
            result_id = f"New player ID: {new_id}"
            result_codename = f"Codename: {codename}"

    def close_modal():
        nonlocal modal_running
        modal_running = False

    new_player_button = Button(450, 350, 150, 40, "Add New Player", save_new_player)
    close_button = Button(750, 300, 40, 40, "X", close_modal)

    while modal_running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            new_codename_box.handle_event(event)
            new_player_button.handle_event(event)
            close_button.handle_event(event)

        # Base dimensions for the modal box
        base_x, base_y = 400, 250
        base_width, base_height = 400, 150  # Default base height
        modal_box = pygame.Rect(base_x, base_y, base_width, base_height)

        if result_id or result_codename:
            # Calculate the height of the modal box based on the result text
            result_lines = [result_id, result_codename]
            text_height = len(result_lines) * 30
            modal_box.height = base_height + text_height  # Extend height

        pygame.draw.rect(screen, (200, 200, 200), modal_box)  # Light gray box
        pygame.draw.rect(screen, black, modal_box, 2)  # Black border

        # Draw text and buttons inside the modal
        screen.blit(font.render("Enter New Codename:", True, black), (modal_box.x + 10, modal_box.y + 10))
        new_codename_box.draw(screen)
        new_player_button.draw(screen)
        close_button.draw(screen)

        # Draw result text, starting lower down
        y_offset = modal_box.y + 150  # Start drawing the text below the form
        for line in [result_id, result_codename]:
            if line:
                screen.blit(font.render(line, True, black), (modal_box.x + 10, y_offset))
                y_offset += 30  # Move down for the next line

        pygame.display.flip()
        clock.tick(60)

# Player entry screen with two team columns
def player_entry_screen(conn):
    draw_gradient_background(screen)
    draw_neon_lines(screen)
    team1_id_boxes = [TextBox(100, 150 + i * 40, 100, 30) for i in range(15)]
    team1_codename_boxes = [TextBox(250, 150 + i * 40, 150, 30, readonly=True) for i in range(15)]
    team2_id_boxes = [TextBox(700, 150 + i * 40, 100, 30) for i in range(15)]
    team2_codename_boxes = [TextBox(850, 150 + i * 40, 150, 30, readonly=True) for i in range(15)]

    def submit_team():
        for i, box in enumerate(team1_id_boxes):
            if box.text:
                codename = fetch_codename_from_db(box.text, conn)
                team1_codename_boxes[i].text = codename
                team1_codename_boxes[i].txt_surface = font.render(codename, True, black)
        for i, box in enumerate(team2_id_boxes):
            if box.text:
                codename = fetch_codename_from_db(box.text, conn)
                team2_codename_boxes[i].text = codename
                team2_codename_boxes[i].txt_surface = font.render(codename, True, black)

    team1_color = "White"
    team2_color = "White"
    
    dropdown_menu_team1 = DropdownMenu(100, 80, 95, 36, dropdown_colors)
    dropdown_menu_team2 = DropdownMenu(700, 80, 95, 36, dropdown_colors)
    
    team_submit_button = Button(400, 750, 200, 50, "Submit", submit_team)
    add_new_player_button = Button(620, 750, 200, 50, "Add New Player", lambda: show_new_player_menu(conn))
    view_database_button = Button(850, 750, 200, 50, "View Database", lambda: show_database_menu(conn))

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            for box in team1_id_boxes + team2_id_boxes:
                box.handle_event(event)
            
            team_submit_button.handle_event(event)
            add_new_player_button.handle_event(event)
            view_database_button.handle_event(event)
            dropdown_menu_team1.handle_event(event)
            dropdown_menu_team2.handle_event(event)
            
            team1_color = dropdown_menu_team1.selected_option
            team2_color = dropdown_menu_team2.selected_option

        screen.fill(black)
        draw_gradient_background(screen)
        draw_neon_lines(screen)

        team1_rgb = dropdown_colors[team1_color]
        team2_rgb = dropdown_colors[team2_color]

        team1_text_color = get_contrasting_color(team1_rgb)
        team2_text_color = get_contrasting_color(team2_rgb)
        team1_border_color = team1_text_color
        team2_border_color = team2_text_color

        pygame.draw.rect(screen, team1_rgb, pygame.Rect(90, 70, 325, 680))
        pygame.draw.rect(screen, team2_rgb, pygame.Rect(690, 70, 325, 680))

        for i in range(15):
            team1_id_boxes[i].draw(screen, border_color=team1_border_color)
            team1_codename_boxes[i].draw(screen, border_color=team1_border_color)
            team2_id_boxes[i].draw(screen, border_color=team2_border_color)
            team2_codename_boxes[i].draw(screen, border_color=team2_border_color)

        screen.blit(font.render("Team 1", True, black), (200, 90))
        screen.blit(font.render("ID", True, black), (145, 115))
        screen.blit(font.render("Codename", True, black), (250, 115))
        screen.blit(font.render("Team 2", True, black), (800, 90))
        screen.blit(font.render("ID", True, black), (745, 115))
        screen.blit(font.render("Codename", True, black), (850, 115))
        
        dropdown_menu_team1.draw(screen)
        dropdown_menu_team2.draw(screen)
        team_submit_button.draw(screen)
        add_new_player_button.draw(screen)
        view_database_button.draw(screen)

        pygame.display.flip()
        clock.tick(60)


def show_splash_screen():
    clock = pygame.time.Clock()
    running = True
    laser_positions = []

    # Load and resize logo image
    logo_image = load_image("logo.jpg")
    
    # Resize the logo to be 60% of the screen size (adjust the percentage as needed)
    logo_width = int(screen_width * 0.6)
    logo_height = int(screen_height * 0.6)
    logo_image = pygame.transform.scale(logo_image, (logo_width, logo_height))
    
    # Create a new surface for the border
    border_thickness = 10  # Adjust the border thickness as needed
    logo_with_border = pygame.Surface((logo_width + 2 * border_thickness, logo_height + 2 * border_thickness))
    
    # Fill the new surface with white for the border
    logo_with_border.fill(white)
    
    # Blit the logo onto the white surface, centered inside the border
    logo_with_border.blit(logo_image, (border_thickness, border_thickness))
    
    # Get the rectangle of the bordered image and center it
    logo_rect = logo_with_border.get_rect(center=(screen_width // 2, screen_height // 2))

    # Generate 10 random lasers
>>>>>>> ed3f4e1a6fa634f57d892939faef75d57cfbcc0e
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

