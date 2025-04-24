from flask import Flask, render_template, request, jsonify, send_from_directory, redirect
from flask_cors import CORS
import sqlite3
from datetime import datetime
from contextlib import contextmanager
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini with valid model
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")  # use supported model

# Initialize Flask
app = Flask(__name__, template_folder='.')
CORS(app)

# SQLite database config
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

@app.route('/static/<path:path>')
def serve_static(path):
    return send_from_directory('static', path)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

@app.route('/about')
@app.route('/doctors')
@app.route('/contact')
@app.route('/appointments')
def redirect_home():
    return redirect('/') 

# ✅ Gemini Chatbot Integration
# Track basic logic manually
@app.route('/api/check-symptoms', methods=['POST'])
def check_symptoms():
    user_input = request.json.get("input", "").lower()

    try:
        # If user wants to book an appointment
        if any(keyword in user_input for keyword in ["book", "appointment", "doctor", "visit"]):
            reply = (
                "Sure! To book an appointment, please provide:\n"
                "1. Department (e.g., Cardiology, Dermatology)\n"
                "2. Doctor Name\n"
                "3. Date (e.g., 2025-04-25)\n"
                "4. Time (e.g., 10:00 AM)\n"
                "5. Your Name, Email, Phone, and symptoms."
            )
            return jsonify({"success": True, "response": reply})
        
        # General symptom Q&A via Gemini
        prompt = f"You are a concise and friendly medical assistant. Answer briefly: {user_input}"
        response = model.generate_content(prompt)
        reply = (response.text or '').strip()
        if not reply:
            reply = "Sorry, I couldn't understand that."
        return jsonify({"success": True, "response": reply})

    except Exception as e:
        return jsonify({"success": False, "response": f"Gemini Error: {e}"}), 500


# Department/Doctors/Appointment APIs (unchanged)
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
    try:
        data = request.json
        date = data.get('date')
        doctor = data.get('doctor')
        morning_slots = [f"{hour}:00 AM" for hour in range(9, 12)]
        afternoon_slots = [f"{hour}:00 PM" for hour in range(1, 6)]
        all_slots = morning_slots + afternoon_slots
        available_slots = []
        with get_db() as conn:
            cursor = conn.cursor()
            for slot in all_slots:
                cursor.execute('''
                    SELECT COUNT(*) FROM appointments 
                    WHERE doctor = ? AND date = ? AND time = ? AND status = 'confirmed'
                ''', (doctor, date, slot))
                if cursor.fetchone()[0] == 0:
                    available_slots.append(slot)
        return jsonify(available_slots)
    except Exception as e:
        return jsonify({'error': f'Error fetching time slots: {str(e)}'}), 500

@app.route('/api/check-availability', methods=['POST'])
def check_availability():
    try:
        data = request.json
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) FROM appointments 
                WHERE doctor = ? AND date = ? AND time = ? AND status = 'confirmed'
            ''', (data['doctor'], data['date'], data['time']))
            count = cursor.fetchone()[0]
            return jsonify({'available': count == 0})
    except Exception as e:
        return jsonify({'error': f'Error checking availability: {str(e)}'}), 500

@app.route('/api/book-appointment', methods=['POST'])
def book_appointment():
    try:
        data = request.json
        required_fields = ['department', 'doctor', 'date', 'time', 'name', 'email', 'phone', 'symptoms']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Missing field: {field}'}), 400
        appointment_id = f"{data['doctor']}_{data['date']}_{data['time']}".replace(" ", "_").replace(":", "-")
        with get_db() as conn:
            conn.execute('''
                INSERT INTO appointments (
                    id, department, doctor, date, time,
                    patient_name, patient_email, patient_phone,
                    status, symptoms
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                appointment_id,
                data['department'],
                data['doctor'],
                data['date'],
                data['time'],
                data['name'],
                data['email'],
                data['phone'],
                'confirmed',
                data['symptoms']
            ))
        return jsonify({'success': True, 'appointment_id': appointment_id})
    except Exception as e:
        return jsonify({'error': f'Error booking appointment: {str(e)}'}), 500

# Run the Flask app
if __name__ == '__main__':
    init_db()
    app.run(debug=True, port=5001)
