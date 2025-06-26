import sqlite3

# Connect to the database
conn = sqlite3.connect("voting_system.db")
cursor = conn.cursor()

# Fetch and display all records from the 'voters' table
cursor.execute("SELECT * FROM voters")
voter_rows = cursor.fetchall()

print("Voter Database:")
for row in voter_rows:
    print(row)

# Fetch and display all records from the 'candidates' table
cursor.execute("SELECT * FROM candidates")
candidate_rows = cursor.fetchall()

print("\nCandidate Database:")
for row in candidate_rows:
    print(row)

# Fetch and display all records from the 'votes' table
cursor.execute("SELECT * FROM votes")
votes_rows = cursor.fetchall()

print("\nVotes Database:")
for row in votes_rows:
    print(row)

conn.close()