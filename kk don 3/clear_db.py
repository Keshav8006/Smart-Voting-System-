import sqlite3

def clear_database_tables():
    try:
        conn = sqlite3.connect("voting_system.db")
        cursor = conn.cursor()

        # Delete all entries from the 'voters' table
        cursor.execute("DELETE FROM voters")
        print("All entries deleted from the 'voters' table.")

        # Delete all entries from the 'candidates' table
        cursor.execute("DELETE FROM candidates")
        print("All entries deleted from the 'candidates' table.")

        conn.commit()
        conn.close()
        print("Database changes committed.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if conn:
            conn.close()

# Call the function to clear the tables
clear_database_tables()