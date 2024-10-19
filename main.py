import tkinter as tk
from database import Database
from udp_communication import UDPCommunication
from splash_screen import SplashScreen
from setup_screen import SetupScreen
from play_action_screen import PlayActionScreen
import atexit

def main():
    # Initialize the main Tkinter window
    root = tk.Tk()
    root.withdraw()  # Hide the main window initially

    # Initialize database connection
    database = Database()

    # Initialize UDP Communication
    try:
        udp_comm = UDPCommunication(broadcast_port=7500, receive_port=7501)
    except OSError:
        print("Failed to bind UDP ports. Make sure no other application is using these ports.")
        return

    # Show splash screen
    splash = SplashScreen(root, "Images/logo.jpg", duration=3000)

    # After splash screen, show setup screen
    def show_setup_screen():
        root.deiconify()  # Show the main window
        SetupScreen(root, database, udp_comm, start_game)

    root.after(3000, show_setup_screen)  # Schedule to show setup screen after splash

    # Function to start the game (open Play Action Screen)
    def start_game(red_team, blue_team):
        countdown_time = 10  # 10 seconds countdown
        timer_label = tk.Label(root, font=("Helvetica", 48))
        timer_label.pack()  # Add the label to the window

        def update_timer(remaining):
            if remaining > 0:
                timer_label.config(text=str(remaining))  # Update the label with remaining time
                root.after(1000, update_timer, remaining - 1)  # Schedule the next update after 1 second
            else:
                udp_comm.send_broadcast("202")  # Send the 202 broadcast message
                PlayActionScreen(root, udp_comm, red_team, blue_team)  # Start the game


    # Handle application exit to ensure sockets are closed
    def on_close():
        udp_comm.close_sockets()
        database.close()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    # Register cleanup in case of unexpected exits
    atexit.register(on_close)

    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    main()

