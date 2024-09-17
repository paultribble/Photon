import pygame
import psycopg2
import sys
import random
import os
import math

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Photon Laser Tag")

scroll_offset = 0

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

# Fetch codename from database based on ID
def fetch_codename_from_db(player_id, conn):
    cursor = conn.cursor()
    cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
    result = cursor.fetchone()
    if result:
        return result[0]
    return ""

# Add new player to the database with a random unique ID
def add_new_player(conn, codename):
    cursor = conn.cursor()
    while True:
        new_id = random.randint(1, 999999)
        cursor.execute("SELECT * FROM players WHERE id = %s", (new_id,))
        if cursor.fetchone() is None:
            cursor.execute("INSERT INTO players (id, codename) VALUES (%s, %s)", (new_id, codename))
            conn.commit()
            return new_id

# New Player Menu
def show_new_player_menu(conn):
    running = True
    new_codename_box = TextBox(500, 400, 200, 40)

    def save_new_player():
        codename = new_codename_box.text
        if codename:
            new_id = add_new_player(conn, codename)
            result_text = f"New player added with ID: {new_id} and Codename: {codename}"
            print(result_text)
            new_codename_box.text = result_text
            new_codename_box.txt_surface = font.render(result_text, True, black)

    new_player_button = Button(500, 500, 200, 50, "Add New Player", save_new_player)
    close_button = Button(650, 350, 50, 50, "X", lambda: setattr(new_player_menu, 'running', False))
    clock = pygame.time.Clock()

    new_player_menu = type('Menu', (object,), {'running': running})()  # Use dynamic attribute

    while new_player_menu.running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            new_codename_box.handle_event(event)
            new_player_button.handle_event(event)
            close_button.handle_event(event)

        screen.fill(white)
        screen.blit(font.render("Enter New Codename:", True, black), (500, 350))
        new_codename_box.draw(screen)
        new_player_button.draw(screen)
        close_button.draw(screen)
        pygame.display.flip()
        clock.tick(30)

# Player entry screen with two team columns
def player_entry_screen(conn, scroll_offset):
    
    scroll_offset += 2
    
    draw_gradient_background(screen, top_color, bottom_color)
    draw_neon_lines(screen, neon_color, 4, pygame.time.get_ticks())
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

    # Color selected for each team
    team1_color = "White"
    team2_color = "White"
    
    # Dropdown menus for team colors
    dropdown_menu_team1 = DropdownMenu(100, 80, 95, 36, dropdown_colors)
    dropdown_menu_team2 = DropdownMenu(700, 80, 95, 36, dropdown_colors)
    
    team_submit_button = Button(500, 750, 200, 50, "Submit", submit_team)
    add_new_player_button = Button(500, 810, 200, 50, "Add New Player", lambda: show_new_player_menu(conn))
    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

            # Handle text box events
            for box in team1_id_boxes + team2_id_boxes:
                box.handle_event(event)
            
            # Handle button events
            team_submit_button.handle_event(event)
            add_new_player_button.handle_event(event)
            
            # Handle dropdown menu events
            dropdown_menu_team1.handle_event(event)
            dropdown_menu_team2.handle_event(event)
            
            # Update selected team colors
            team1_color = dropdown_menu_team1.selected_option
            team2_color = dropdown_menu_team2.selected_option

        ##screen.fill(white)

        # Get RGB values for selected colors
        team1_rgb = dropdown_colors[team1_color]
        team2_rgb = dropdown_colors[team2_color]

        # Determine contrasting colors for text and borders
        team1_text_color = get_contrasting_color(team1_rgb)
        team2_text_color = get_contrasting_color(team2_rgb)
        team1_border_color = team1_text_color  # Make border same as text color
        team2_border_color = team2_text_color

        # Draw team backgrounds with selected colors
        pygame.draw.rect(screen, team1_rgb, pygame.Rect(90, 70, 325, 680))
        pygame.draw.rect(screen, team2_rgb, pygame.Rect(690, 70, 325, 680))

        # Draw text boxes for both teams with contrasting borders
        for i in range(15):
            team1_id_boxes[i].draw(screen, border_color=team1_border_color)
            team1_codename_boxes[i].draw(screen, border_color=team1_border_color)
            team2_id_boxes[i].draw(screen, border_color=team2_border_color)
            team2_codename_boxes[i].draw(screen, border_color=team2_border_color)

        # Render team labels and input fields with contrasting text color
        screen.blit(font.render("Team 1", True, black), (200, 90))
        screen.blit(font.render("ID", True, black), (145, 115))
        screen.blit(font.render("Codename", True, black), (250, 115))
        screen.blit(font.render("Team 2", True, black), (800, 90))
        screen.blit(font.render("ID", True, black), (745, 115))
        screen.blit(font.render("Codename", True, black), (850, 115))
        
        # Draw dropdown menus
        dropdown_menu_team1.draw(screen)
        dropdown_menu_team2.draw(screen)

        # Draw buttons
        team_submit_button.draw(screen)
        add_new_player_button.draw(screen)

        pygame.display.flip()
        clock.tick(30)




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
    for _ in range(30):
        start_pos = (random.randint(0, screen_width), random.randint(0, screen_height))
        end_pos = (random.randint(0, screen_width), random.randint(0, screen_height))
        laser_positions.append((start_pos, end_pos))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

        screen.fill(black)

        # Draw the laser animations
        for start_pos, end_pos in laser_positions:
            pygame.draw.line(screen, red, start_pos, end_pos, 2)

        # Draw the logo with the white border
        screen.blit(logo_with_border, logo_rect)

        pygame.display.flip()
        clock.tick(30)

        pygame.time.delay(3000)  # Display splash screen for 3 seconds
        running = False

def draw_gradient_background(screen, top_color, bottom_color):
    """Draws a vertical gradient from top_color to bottom_color."""
    for y in range(screen_height):
        ratio = y / screen_height
        color = (
            int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio),
            int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio),
            int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        )
        pygame.draw.line(screen, color, (0, y), (screen_width, y))

# Example usage
top_color = (10, 10, 200)  # Dark blue
bottom_color = (0, 0, 0)   # Black
draw_gradient_background(screen, top_color, bottom_color)





def draw_neon_lines(screen, color, line_thickness, time):
    """Draws glowing neon lines that pulse."""
    amplitude = 10
    for i in range(0, screen_width, 100):
        offset = amplitude * math.sin(time / 500.0 + i)
        pygame.draw.line(screen, color, (i, 300 + offset), (i, screen_height), line_thickness)

# Example usage
neon_color = (255, 0, 255)  # Neon pink
line_thickness = 4
draw_neon_lines(screen, neon_color, line_thickness, pygame.time.get_ticks())

def draw_moving_stripes(screen, stripe_color, stripe_width, scroll_offset):
    """Draws moving stripes across the background."""
    for i in range(0, screen_width, stripe_width * 2):
        pygame.draw.rect(screen, stripe_color, (i - scroll_offset % (stripe_width * 2), 0, stripe_width, screen_height))

# Example usage
stripe_color = (255, 0, 0)  # Red stripes
stripe_width = 20
draw_moving_stripes(screen, stripe_color, stripe_width, scroll_offset)




def main():
    show_splash_screen()
    conn = connect_to_database()
    player_entry_screen(conn, scroll_offset)

if __name__ == "__main__":
    main()
