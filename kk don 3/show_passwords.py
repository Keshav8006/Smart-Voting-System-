import sqlite3

def display_candidate_passwords():
    try:
        conn = sqlite3.connect("voting_system.db")
        cursor = conn.cursor()

        cursor.execute("SELECT candidate_id, password FROM candidates")
        rows = cursor.fetchall()

        conn.close()

        if rows:
            print("Candidate IDs and Hashed Passwords:")
            for candidate_id, password in rows:
                print(f"  Candidate ID: {candidate_id}")
                print(f"  Hashed Password: {password}")
                print("-" * 30)
        else:
            print("No candidates found in the database.")

    except sqlite3.Error as e:
        print(f"Error accessing the database: {e}")

if __name__ == "__main__":
    display_candidate_passwords()