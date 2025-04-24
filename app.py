from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
import sqlite3
from contextlib import contextmanager
import os
from dotenv import load_dotenv
import google.generativeai as genai

# ─── Load env & configure Gemini ──────────────────────────────────────────────
load_dotenv()
GEMINI_API_KEY   = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL     = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

# ─── Flask + CORS setup ───────────────────────────────────────────────────────
app = Flask(__name__, template_folder='.')
CORS(app)

# ─── SQLite config ────────────────────────────────────────────────────────────
DATABASE = 'medical_appointments.db'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id TEXT PRIMARY KEY,
                department TEXT,
                doctor TEXT,
                date TEXT,
                time TEXT,
                patient_name TEXT,
                patient_email TEXT,
                patient_phone TEXT,
                status TEXT,
                symptoms TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    try:
        yield conn
    finally:
        conn.close()

# initialize DB
init_db()

# ─── Static / Page routes ─────────────────────────────────────────────────────
@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

# redirect old links
@app.route('/about')
@app.route('/doctors')
@app.route('/contact')
@app.route('/appointments')
def redirect_home():
    return redirect('/')

# ─── AI Q&A endpoint ──────────────────────────────────────────────────────────
@app.route('/api/check-symptoms', methods=['POST'])
def check_symptoms():
    user_input = request.json.get("input", "").strip()
    # build prompt
    prompt = (
        "You are a concise, friendly medical assistant. Answer the user’s question or "
        "give brief advice. If you don’t understand, say so.\n\n"
        "User: " + user_input + "\nAssistant:"
    )
    try:
        response = model.generate_content(prompt)
        reply = (response.text or "").strip()
        if not reply:
            reply = "Sorry, I couldn't process that."
        return jsonify({"success": True, "response": reply})
    except Exception as e:
        return jsonify({"success": False, "response": f"Gemini Error: {e}"}), 500

# ─── Booking support endpoints ─────────────────────────────────────────────────
@app.route('/api/get-departments')
def get_departments():
    return jsonify([
        'Cardiology', 'Orthopedics', 'Pediatrics', 'General Medicine',
        'Dermatology', 'Neurology', 'Gynecology', 'Dentistry'
    ])

@app.route('/api/get-doctors/<department>')
def get_doctors(department):
    doctors_db = {
        'Cardiology': ['Dr. Smith (Cardiologist)', 'Dr. Johnson (Heart Specialist)'],
        'Orthopedics': ['Dr. Williams (Bone Specialist)', 'Dr. Brown (Joint Specialist)'],
        'Pediatrics': ['Dr. Davis (Child Specialist)', 'Dr. Miller (Pediatrician)'],
        'General Medicine': ['Dr. Wilson (General Physician)', 'Dr. Moore (Family Doctor)'],
        'Dermatology': ['Dr. Taylor (Skin Specialist)', 'Dr. Anderson (Dermatologist)'],
        'Neurology': ['Dr. Thomas (Neurologist)', 'Dr. White (Brain Specialist)'],
        'Gynecology': ['Dr. Martinez (Gynecologist)', 'Dr. Garcia (Women\'s Health)'],
        'Dentistry': ['Dr. Clark (Dentist)', 'Dr. Lewis (Dental Surgeon)']
    }
    return jsonify(doctors_db.get(department, []))

@app.route('/api/get-time-slots', methods=['POST'])
def get_time_slots():
    data = request.json
    date = data.get('date')
    doctor = data.get('doctor')
    morning = [f"{h}:00 AM" for h in range(9,12)]
    afternoon = [f"{h}:00 PM" for h in range(1,6)]
    slots = morning + afternoon
    available = []
    with get_db() as conn:
        cur = conn.cursor()
        for s in slots:
            cur.execute('''
                SELECT COUNT(*) FROM appointments 
                WHERE doctor=? AND date=? AND time=? AND status='confirmed'
            ''', (doctor, date, s))
            if cur.fetchone()[0] == 0:
                available.append(s)
    return jsonify(available)

@app.route('/api/book-appointment', methods=['POST'])
def book_appointment():
    data = request.json
    required = ['department','doctor','date','time','name','email','phone','symptoms']
    for f in required:
        if not data.get(f):
            return jsonify({'success': False, 'error': f'Missing field: {f}'}), 400
    aid = f"{data['doctor']}_{data['date']}_{data['time']}".replace(" ", "_").replace(":","-")
    with get_db() as conn:
        conn.execute('''
            INSERT INTO appointments (
                id, department, doctor, date, time,
                patient_name, patient_email, patient_phone,
                status, symptoms
            ) VALUES (?,?,?,?,?,?,?,?,?,?)
        ''', (
            aid, data['department'], data['doctor'], data['date'], data['time'],
            data['name'], data['email'], data['phone'],
            'confirmed', data['symptoms']
        ))
    return jsonify({'success': True, 'appointment_id': aid})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
