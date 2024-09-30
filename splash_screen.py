# splash_screen.py
import tkinter as tk
from PIL import Image, ImageTk

class SplashScreen:
    def __init__(self, parent, image_path, duration=3000):
        self.parent = parent
        self.splash = tk.Toplevel(parent)
        self.splash.title("Welcome to Photon Laser Tag!")
        self.splash.geometry("400x300")
        self.splash.configure(bg='black')
        self.splash.overrideredirect(True)  # Remove window decorations

        try:
            logo_image = Image.open(image_path)
            logo_image = logo_image.resize((300, 200), Image.LANCZOS)
            logo_photo = ImageTk.PhotoImage(logo_image)
            label = tk.Label(self.splash, image=logo_photo, bg='black')
            label.image = logo_photo  # Keep a reference
            label.pack(expand=True)
        except Exception as e:
            label = tk.Label(self.splash, text="Photon Laser Tag", bg='black', fg='white', font=("Arial", 20))
            label.pack(expand=True)

        self.parent.after(duration, self.close_splash)

    def close_splash(self):
        self.splash.destroy()
