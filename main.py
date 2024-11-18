import tkinter as tk
from database import Database
from udp_communication import UDPCommunication
from splash_screen import SplashScreen
from setup_screen import SetupScreen
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

    # Declare setup_screen so it is accessible in on_close
    setup_screen = None  # Initial value is None

    # After splash screen, show setup screen
    def show_setup_screen():
        nonlocal setup_screen  # Access the outer scope variable
        root.deiconify()  # Show the main window
        setup_screen = SetupScreen(root, database, udp_comm)

    root.after(3000, show_setup_screen)  # Schedule to show setup screen after splash

    # Handle application exit to ensure sockets are closed
    def on_close():
        print("on_close triggered")
        nonlocal setup_screen  # Access the outer scope variable
        if setup_screen:  # Check if setup_screen has been initialized
            print("Stopping music...")
            setup_screen.stop_music()
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
