import pygame
import psycopg2
import sys
import random
import os

# Initialize Pygame
pygame.init()

# Set up display
screen_width = 1200
screen_height = 800
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Laser Tag Player Entry")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
gray = (200, 200, 200)
blue = (0, 0, 255)
red = (255, 0, 0)

# Fonts
font = pygame.font.Font(None, 36)

# Load logo image
def load_image(filename):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    image_path = os.path.join(script_dir, "Images", filename)
    return pygame.image.load(image_path)

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

# TextBox class for player input
class TextBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = gray
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.txt_surface = self.font.render(text, True, black)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the user clicked on the input box
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = blue if self.active else gray

        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
                self.txt_surface = self.font.render(self.text, True, black)

    def draw(self, screen):
        # Render the text
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        pygame.draw.rect(screen, self.color, self.rect, 2)

# Button class for handling button clicks
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

# Function to save player data to the database
def save_player_data(player_id, nickname, conn):
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO players (id, codename) VALUES (%s, %s)",
            (player_id, nickname)
        )
        conn.commit()
    except psycopg2.IntegrityError:
        conn.rollback()
        cursor.execute(
            "UPDATE players SET codename = %s WHERE id = %s",
            (nickname, player_id)
        )
        conn.commit()
    except Exception as e:
        print(f"Error saving player data: {e}")

# Splash screen with a simple laser animation
def show_splash_screen():
    clock = pygame.time.Clock()
    running = True
    laser_positions = []

    # Load logo image
    logo_image = load_image("logo.jpg")
    logo_rect = logo_image.get_rect(center=(screen_width // 2, screen_height // 2))

    for _ in range(10):  # Create 10 random lasers
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

        # Draw the logo image
        screen.blit(logo_image, logo_rect)

        pygame.display.flip()
        clock.tick(30)

        pygame.time.delay(3000)  # Display splash screen for 3 seconds
        running = False

# Player entry screen with two team columns
def player_entry_screen(conn):
    # Define positions for input boxes and buttons
    team1_boxes = [TextBox(100, 150 + i * 40, 200, 30) for i in range(15)]
    team2_boxes = [TextBox(700, 150 + i * 40, 200, 30) for i in range(15)]

    def submit_team1():
        for i, box in enumerate(team1_boxes):
            save_player_data(i + 1, box.text, conn)

    def submit_team2():
        for i, box in enumerate(team2_boxes):
            save_player_data(i + 16, box.text, conn)

    team1_button = Button(100, 700, 200, 50, "Submit Team 1", submit_team1)
    team2_button = Button(700, 700, 200, 50, "Submit Team 2", submit_team2)

    clock = pygame.time.Clock()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            for box in team1_boxes + team2_boxes:
                box.handle_event(event)
            team1_button.handle_event(event)
            team2_button.handle_event(event)

        screen.fill(white)

        # Draw labels
        screen.blit(font.render("Team 1", True, black), (100, 100))
        screen.blit(font.render("ID", True, black), (150, 120))
        screen.blit(font.render("Codename", True, black), (250, 120))
        screen.blit(font.render("Team 2", True, black), (700, 100))
        screen.blit(font.render("ID", True, black), (750, 120))
        screen.blit(font.render("Codename", True, black), (850, 120))

        for i, box in enumerate(team1_boxes):
            box.draw(screen)
        for i, box in enumerate(team2_boxes):
            box.draw(screen)

        team1_button.draw(screen)
        team2_button.draw(screen)

        pygame.display.flip()
        clock.tick(30)

def main():
    show_splash_screen()
    conn = connect_to_database()
    player_entry_screen(conn)

if __name__ == "__main__":
    main()
