import csv
from flask import Flask, render_template, request, jsonify
from datetime import datetime
import cv2

app = Flask(__name__, static_url_path='/static')

# Function to save attendance to a CSV file
def save_attendance_to_csv(attendance):
    with open('attendance.csv', 'w', newline='') as csvfile:
        fieldnames = ['Student ID', 'Session Date', 'Session Time', 'Attendance Time']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for key, value in attendance.items():
            student_id, session_date, session_time = key.split('_')
            attendance_time = datetime.strptime(value, "%Y-%m-%d %H:%M:%S").strftime("%H:%M:%S")
            writer.writerow({'Student ID': student_id,
                             'Session Date': session_date,
                             'Session Time': session_time,
                             'Attendance Time': attendance_time})
            
# Load pre-trained face cascade
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


# Function to perform facial recognition
def recognize_face(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    if len(faces) > 0:
        # Assume the first face detected is the student
        return True
    else:
        return False

# Attendance tracking dictionary
attendance = {}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mark_attendance', methods=['POST'])
def mark_attendance():
    student_id = request.form['student_id']
    session_date = request.form['session_date']
    session_time = request.form['session_time']
    attendance_key = f"{student_id}_{session_date}_{session_time}"
    
    if attendance_key in attendance:
        return jsonify({'message': 'Attendance already recorded for this student.'}), 400
    
    # Initialize video capture
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        if recognize_face(frame):
            attendance[attendance_key] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            save_attendance_to_csv(attendance)  # Save attendance to CSV file
            cap.release()
            cv2.destroyAllWindows()
            return jsonify({'message': 'Attendance recorded successfully.'}), 200

    cap.release()
    cv2.destroyAllWindows()
    return jsonify({'message': 'Failed to recognize student.'}), 400

if __name__ == "__main__":
    app.run(debug=False)
