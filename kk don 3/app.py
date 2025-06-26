from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
import cv2
import numpy as np
import random
import string
import bcrypt  # For password hashing

app = Flask(__name__)

# Initialize the database
def initialize_database():
    try:
        conn = sqlite3.connect("voting_system.db")
        cursor = conn.cursor()

        # Create candidates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS candidates (
                candidate_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                face_image_path TEXT NOT NULL
            )
        """)
        print("Candidates table created.")

        # Create voters table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS voters (
                voter_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                face_image_path TEXT NOT NULL
            )
        """)
        print("Voters table checked/created.")

        # Create votes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS votes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                voter_id TEXT NOT NULL,
                candidate_name TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (voter_id) REFERENCES voters(voter_id)
            )
        """)
        print("Votes table checked/created.")

        conn.commit()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Error initializing database: {e}")

       
initialize_database()  # Call the function here 

# Generate random password
def generate_password(length=8):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

# Match face
def match_face(input_face_path, registered_face_path):
    try:
        input_face = cv2.imread(input_face_path, cv2.IMREAD_GRAYSCALE)
        registered_face = cv2.imread(registered_face_path, cv2.IMREAD_GRAYSCALE)

        if input_face is None or registered_face is None:
            return False

        input_face = cv2.resize(input_face, (100, 100))
        registered_face = cv2.resize(registered_face, (100, 100))

        difference = cv2.absdiff(input_face, registered_face)
        score = np.sum(difference)

        return score < 5000  # Threshold for face matching
    except Exception as e:
        print(f"Error in face matching: {e}")
        return False

# Helper function to capture face
def capture_face_from_camera(person_id, role):
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    cap = cv2.VideoCapture(0)

    print("Press 's' to save the face image, 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            return None, "Failed to capture video."

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))

        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        cv2.imshow(f"{role.capitalize()} Registration", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s') and len(faces) == 1:
            save_path = "registered_faces"
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            face = gray[y:y + h, x:x + w]
            face = cv2.resize(face, (100, 100))  # Resize captured face

            face_path = os.path.join(save_path, f"{person_id}.jpg")
            cv2.imwrite(face_path, face)
            cap.release()
            cv2.destroyAllWindows()

            return face_path, None
        elif key == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return None, "Registration cancelled."

# Flask Routes

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/options")
def options():
    return render_template("options.html")

@app.route("/register-options")
def register_options():
    return render_template("register-options.html")

@app.route("/register/<role>")
def register(role):
    if role not in ["voter", "candidate"]:
        return "Invalid role!"
    print(f"Register route - Role: {role}")  # Debugging Line
    return render_template("register.html", role=role)

@app.route("/submit/<role>", methods=["POST"])
def submit(role):
    try:
        person_id = request.form["person_id"]
        name = request.form["name"]
        password = generate_password()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')  # Hashing the password and decoding to string

        # Capture face for registration
        face_path, error = capture_face_from_camera(person_id, role)
        if error:
            return f"Error during registration: {error}"

        # Save voter or candidate to the database
        conn = sqlite3.connect("voting_system.db")
        cursor = conn.cursor()

        if role == "voter":
            table = "voters"  # Assign table here
            print(f"Submit route - Role: {role}, Inserting into voters table")  # Debugging Line
            cursor.execute(f"INSERT INTO {table} (voter_id, name, password, face_image_path) VALUES (?, ?, ?, ?)",
                           (person_id, name, hashed_password, face_path))
            message = f"<h1>Registration successful!</h1><p>Your password is: {password}</p>"
        else:
            table = "candidates"  # Assign table here
            print(f"Submit route - Role: {role}, Inserting into candidates table")  # Debugging Line
            cursor.execute(f"INSERT INTO {table} (candidate_id, name, password, face_image_path) VALUES (?, ?, ?, ?)",
                           (person_id, name, hashed_password, face_path))  # Corrected line
            message = f"<h1>Registration successful!</h1><p>Your password is: {password}</p>"

        conn.commit()
        conn.close()

        print(f"Candidate Registered: ID={person_id}, Name={name}, Hashed Password={hashed_password}")  # Debugging print statement

        return message
    except Exception as e:
        return f"Error during registration: {e}"

@app.route("/voter-login")
def voter_login_page():
    return render_template("voter-login.html")

@app.route("/candidate-login")
def candidate_login_page():
    return render_template("candidate-login.html")

@app.route("/voter_login", methods=["GET", "POST"])
def voter_login():
    if request.method == "POST":
        try:
            voter_id = request.form["voter_id"]
            password = request.form["password"]

            # Capture face for verification
            captured_face, error = capture_face_from_camera(voter_id, "voter")
            if error:
                return f"Error during login: {error}"

            # Query the database for the stored password and face image path
            conn = sqlite3.connect("voting_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT password, face_image_path FROM voters WHERE voter_id = ?", (voter_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                stored_password = result[0]  # This is already a string
                stored_face_path = result[1]

                # Check password using bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')) and match_face(captured_face, stored_face_path):
                    # Store voter_id in session
                    session['voter_id'] = voter_id
                    return redirect(url_for('lets_vote'))  # Redirect to lets-vote page after successful login
                else:
                    return "<h1>Login Failed! ID, password, or face mismatch.</h1><p><a href='/voter-login'>Try Again</a></p>"
            else:
                return "<h1>Login Failed! Voter ID not found.</h1><p><a href='/voter-login'>Try Again</a></p>"

        except Exception as e:
            return f"Error during voter login: {e}"

    return render_template("voter-login.html")

@app.route("/candidate_login", methods=["GET", "POST"])
def candidate_login():
    if request.method == "POST":
        try:
            candidate_id = request.form["candidate_id"]
            password = request.form["password"]

            # Capture face for verification
            captured_face, error = capture_face_from_camera(candidate_id, "candidate")
            if error:
                return f"Error during login: {error}"

            # Query the database for the stored password and face image path
            conn = sqlite3.connect("voting_system.db")
            cursor = conn.cursor()
            cursor.execute("SELECT password, face_image_path FROM candidates WHERE candidate_id = ?", (candidate_id,))
            result = cursor.fetchone()
            conn.close()

            if result:
                stored_password = result[0]  # This is already a string
                stored_face_path = result[1]

                print(f"Candidate ID: {candidate_id}")
                print(f"Entered Password: {password}")
                print(f"Stored Hashed Password: {stored_password}")
                print(f"Captured Face: {captured_face}")
                print(f"Stored Face Path: {stored_face_path}")

                # Check password using bcrypt
                if bcrypt.checkpw(password.encode('utf-8'), stored_password.encode('utf-8')) and match_face(captured_face, stored_face_path):
                    return redirect(url_for('candidate_dashboard'))  # Redirect to candidate_dashboard page after successful login
                else:
                    print("Login failed due to password or face mismatch")
                    return "<h1>Login Failed! ID, password, or face mismatch.</h1><p><a href='/candidate-login'>Try Again</a></p>"
            else:
                print("Candidate ID not found")
                return "<h1>Login Failed! Candidate ID not found.</h1><p><a href='/candidate-login'>Try Again</a></p>"
        except Exception as e:
            return f"Error during candidate login: {e}"

    return render_template("candidate-login.html")

@app.route("/candidate_dashboard")
def candidate_dashboard():
    return render_template("candidate_dashboard.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")

@app.route("/lets-vote")
def lets_vote():
    voter_id = session.get('voter_id')
    if not voter_id:
        return "<h1>Error: Voter ID not found. Please log in again.</h1>"
    try:
        conn = sqlite3.connect("voting_system.db")
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM candidates")
        candidates = cursor.fetchall()
        conn.close()

        # Convert list of tuples to a list of names
        candidate_names = [candidate[0] for candidate in candidates]

        return render_template("lets-vote.html", candidate_names=candidate_names)
    except Exception as e:
        return f"Error fetching candidates: {e}"

@app.route("/submit_vote", methods=["POST"])
def submit_vote():
    try:
        candidate_name = request.form["candidate"]
        voter_id = session.get('voter_id')  # Retrieve voter_id from session

        if not voter_id:
            return "<h1>Error: Voter ID not found. Please log in again.</h1>"

        conn = sqlite3.connect("voting_system.db")
        cursor = conn.cursor()

        # Check if the voter has already voted
        cursor.execute("SELECT COUNT(*) FROM votes WHERE voter_id = ?", (voter_id,))
        vote_count = cursor.fetchone()[0]

        if vote_count > 0:
            conn.close()
            return "<h1>Error: You have already voted.</h1>"  # Display an error message
        else:
            # Insert the vote
            cursor.execute("INSERT INTO votes (voter_id, candidate_name) VALUES (?, ?)", (voter_id, candidate_name))
            conn.commit()
            conn.close()

            return "<h1>Vote submitted successfully!</h1>"  # Display a confirmation message
    except Exception as e:
        return f"Error submitting vote: {e}"

if __name__ == "__main__":
    # Enable session management
    app.secret_key = os.urandom(24)
    app.run(debug=True)