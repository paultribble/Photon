# database.py
import psycopg2
import sys
import random
class Database:
    def __init__(self, dbname="photon", user="student"):
        try:
            self.conn = psycopg2.connect(
                dbname=dbname,
                user=user,
            )
            self.conn.autocommit = True
        except Exception as e:
            print(f"Error connecting to PostgreSQL database: {e}")
            sys.exit(1)

    def get_codename(self, player_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT codename FROM players WHERE id = %s", (player_id,))
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except Exception as e:
            print(f"Database error: {e}")
            return None

    def add_player(self, codename, player_id=None):
        try:
            cursor = self.conn.cursor()
            
            if player_id is None or player_id == "":  # If ID is not provided, generate a random ID
                while True:
                    player_id = random.randint(1, 99)
                    cursor.execute("SELECT * FROM players WHERE id = %s", (player_id,))
                    if cursor.fetchone() is None:
                        break
            
            else:  # If ID is provided, ensure it's unique
                cursor.execute("SELECT * FROM players WHERE id = %s", (player_id,))
                if cursor.fetchone() is not None:
                    print(f"Error: Player ID {player_id} already exists.")
                    cursor.close()
                    return None

            cursor.execute("INSERT INTO players (id, codename) VALUES (%s, %s)", (player_id, codename))
            cursor.close()
            return player_id
        
        except Exception as e:
            print(f"Database error: {e}")
            return None


    def delete_player(self, player_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM players WHERE id = %s", (player_id,))
            cursor.close()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False

    def get_all_players(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, codename FROM players ORDER BY codename ASC")
            players = cursor.fetchall()
            cursor.close()
            return players
        except Exception as e:
            print(f"Database error: {e}")
            return []

    def clear_players(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM players")
            cursor.close()
            return True
        except Exception as e:
            print(f"Database error: {e}")
            return False

    def close(self):
        if self.conn:
            self.conn.close()
