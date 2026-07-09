import sqlite3
import os
import uuid
from datetime import datetime
from flask import Flask, request, render_template

app = Flask(__name__)

# Upload folder create panradhu
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Database create panradhu
def init_db():
    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS complaints
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  phone TEXT,
                  address TEXT,
                  problem_type TEXT,
                  description TEXT,
                  photo TEXT,
                  voice TEXT,
                  status TEXT,
                  timestamp TEXT)''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    phone = request.form['phone']
    address = request.form['location'] # FIX: address ah correct pannen
    problem_type = request.form['problem_type']
    description = request.form['description']

    # Photo save panradhu
    photo = request.files['photo']
    photo_filename = None
    if photo and photo.filename!= '':
        photo_filename = str(uuid.uuid4()) + '_' + photo.filename
        photo.save(os.path.join(app.config['UPLOAD_FOLDER'], photo_filename))

    # Voice save panradhu
    voice = request.files['voice']
    voice_filename = None
    if voice and voice.filename!= '':
        voice_filename = str(uuid.uuid4()) + '_' + voice.filename
        voice.save(os.path.join(app.config['UPLOAD_FOLDER'], voice_filename))

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    status = "Pending"

    # Database la save panradhu - FIX: line break remove pannen
    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    c.execute("INSERT INTO complaints (name, phone, address, problem_type, description, photo, voice, status, timestamp) VALUES (?,?,?,?,?,?,?,?,?)",
              (name, phone, address, problem_type, description, photo_filename, voice_filename, status, timestamp))
    conn.commit()
    complaint_id = c.lastrowid # Pudhu ID ah eduthukrom
    conn.close()

    return f"""
    <h1>Complaint Submitted Successfully! / புகார் வெற்றிகரமாக சமர்பிக்கப்பட்டது!</h1>
    <h2 style='color: red;'>Your Complaint ID: {complaint_id}</h2>
    <h2 style='color: red;'>உங்கள் புகார் ID: {complaint_id}</h2>
    <p><b>Please save this ID. / இந்த ID ஐ சேவ் செய்து வைக்கவும்</b></p>
    <a href='/'>Submit Another</a> | <a href='/status'>Check Status</a>
    """

@app.route('/admin')
def admin():
    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    c.execute("SELECT * FROM complaints ORDER BY timestamp DESC")
    complaints = c.fetchall()
    conn.close()
    return render_template('admin.html', complaints=complaints)

@app.route('/solve/<int:id>')
def solve(id):
    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    c.execute("UPDATE complaints SET status = 'Solved' WHERE id =?", (id,)) # FIX: space potuten
    conn.commit()
    conn.close()
    return "Complaint marked as Solved! <a href='/admin'>Go Back</a>"

@app.route('/status')
def status():
    return """
<!DOCTYPE html>
<html lang="ta">
<head>
    <meta charset="UTF-8">
    <title>Status Check</title>
</head>
<body>
    <h1>Complaint Status Check / புகார் நிலை சரிபார்க்க</h1>
    <form action="/check_status" method="POST">
        <label>Complaint ID:</label><br>
        <input type="number" name="complaint_id" required><br><br>

        <label>Name / பெயர்:</label><br>
        <input type="text" name="name" required><br><br>

        <button type="submit">Check</button>
    </form>
</body>
</html>
"""

@app.route('/check_status', methods=['POST'])
def check_status():
    complaint_id = request.form['complaint_id']
    name = request.form['name'] # Name um vaangiruvom

    conn = sqlite3.connect('complaints.db')
    c = conn.cursor()
    # ID and Name rendu perum correct ah irukanum
    c.execute("SELECT * FROM complaints WHERE id =? AND name =?", (complaint_id, name)) # FIX: space
    data = c.fetchone()
    conn.close()

    if data:
        return f"<h1>Status: {data[8]}</h1><p>ID: {data[0]}</p><p>Name: {data[1]}</p><p>Description: {data[5]}</p><a href='/status'>Back</a>"
    else:
        return "Complaint not found. ID and Name check pannunga"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')