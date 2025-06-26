import sqlite3

# Connect to the database
conn = sqlite3.connect("voting_system.db")
cursor = conn.cursor()

# Fetch and display all records from the 'voters' table
cursor.execute("SELECT * FROM voters")
rows = cursor.fetchall()

print("Voter Database:")
for row in rows:
    print(row)

conn.close()