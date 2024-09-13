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
pygame.display.set_caption("Photon Laser Tag")

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

# TextBox class for player input
class TextBox:
    def __init__(self, x, y, w, h, text='', readonly=False):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = gray
        self.text = text
        self.font = pygame.font.Font(None, 36)
        self.txt_surface = self.font.render(text, True, black)
        self.active = False
        self.readonly = readonly

    def handle_event(self, event):
        if not self.readonly:
            if event.type == pygame.MOUSEBUTTONDOWN:
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
            print(f"New player added with ID: {new_id} and Codename: {codename}")
        running = False

    new_player_button = Button(500, 500, 200, 50, "Add New Player", save_new_player)
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            new_codename_box.handle_event(event)
            new_player_button.handle_event(event)

        screen.fill(white)
        screen.blit(font.render("Enter New Codename:", True, black), (500, 350))
        new_codename_box.draw(screen)
        new_player_button.draw(screen)
        pygame.display.flip()
        clock.tick(30)

# Player entry screen with two team columns
def player_entry_screen(conn):
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

    team_submit_button = Button(500, 700, 200, 50, "Submit", submit_team)
    add_new_player_button = Button(500, 750, 200, 50, "Add New Player", lambda: show_new_player_menu(conn))
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

        screen.fill(white)
        screen.blit(font.render("Team 1", True, black), (100, 100))
        screen.blit(font.render("ID", True, black), (150, 120))
        screen.blit(font.render("Codename", True, black), (250, 120))
        screen.blit(font.render("Team 2", True, black), (700, 100))
        screen.blit(font.render("ID", True, black), (750, 120))
        screen.blit(font.render("Codename", True, black), (850, 120))

        for i in range(15):
            team1_id_boxes[i].draw(screen)
            team1_codename_boxes[i].draw(screen)
            team2_id_boxes[i].draw(screen)
            team2_codename_boxes[i].draw(screen)

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
    logo_image = resize_image(logo_image, screen_width, screen_height)
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



def main():
    show_splash_screen()
    conn = connect_to_database()
    player_entry_screen(conn)

if __name__ == "__main__":
    main()
