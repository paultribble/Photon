# database_screen.py
import tkinter as tk
from tkinter import messagebox

class DatabaseScreen:
    def __init__(self, parent, database):
        self.parent = parent
        self.database = database

        self.db_window = tk.Toplevel(parent)
        self.db_window.title("Player Database")
        self.db_window.geometry("400x600")

        self.create_widgets()

    def create_widgets(self):
        players = self.database.get_all_players()

        for i, (player_id, codename) in enumerate(players):
            tk.Label(self.db_window, text=f"{player_id}: {codename}").grid(row=i, column=0, padx=10, pady=5, sticky='w')
            delete_button = tk.Button(
                self.db_window,
                text="Delete",
                command=lambda pid=player_id: self.delete_player(pid)
            )
            delete_button.grid(row=i, column=1, padx=10, pady=5)

    def delete_player(self, player_id):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete Player ID {player_id}?")
        if confirm:
            success = self.database.delete_player(player_id)
            if success:
                messagebox.showinfo("Success", f"Player ID {player_id} has been deleted.")
                self.db_window.destroy()
                self.__init__(self.parent, self.database)  # Refresh the database screen
            else:
                messagebox.showerror("Error", "Failed to delete the player.")