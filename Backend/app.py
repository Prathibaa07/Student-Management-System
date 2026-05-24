from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

DB_PATH = 'studentdb.sqlite'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # Enforce foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            rollno TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT,
            email TEXT,
            tenth_marks REAL,
            twelfth_marks REAL,
            current_cgpa REAL NOT NULL,
            backlogs INTEGER DEFAULT 0,
            placed TEXT DEFAULT 'No',
            company_name TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS semester_marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rollno TEXT,
            semester INTEGER,
            gpa REAL,
            FOREIGN KEY (rollno) REFERENCES students(rollno) ON DELETE CASCADE
        )
    ''')
    conn.commit()
    conn.close()

# Initialize tables when the app starts
init_db()

@app.route('/student', methods=['POST'])
def add_student():
    data = request.json
    for key in data:
        if data[key] == "":
            data[key] = None
            
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # UPSERT syntax in SQLite
        query = """
            INSERT INTO students (rollno, name, department, email, tenth_marks, twelfth_marks, current_cgpa, backlogs, placed, company_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(rollno) DO UPDATE SET 
            name=excluded.name, department=excluded.department, email=excluded.email, 
            tenth_marks=excluded.tenth_marks, twelfth_marks=excluded.twelfth_marks, 
            current_cgpa=excluded.current_cgpa, backlogs=excluded.backlogs, 
            placed=excluded.placed, company_name=excluded.company_name
        """
        values = (data['rollno'], data['name'], data.get('department'), data.get('email'), data.get('tenth_marks'), 
                  data.get('twelfth_marks'), data['current_cgpa'], data.get('backlogs', 0), data.get('placed', 'No'), data.get('company_name'))
        cursor.execute(query, values)
        
        if 'semesters' in data:
            cursor.execute("DELETE FROM semester_marks WHERE rollno=?", (data['rollno'],))
            sem_query = "INSERT INTO semester_marks (rollno, semester, gpa) VALUES (?, ?, ?)"
            sem_values = [(data['rollno'], sem['semester'], sem['gpa']) for sem in data['semesters']]
            cursor.executemany(sem_query, sem_values)
            
        conn.commit()
        return jsonify({"message": "Student data saved successfully!"}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route('/student/<identifier>', methods=['GET'])
def get_student(identifier):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM students WHERE rollno=? OR name LIKE ?"
        cursor.execute(query, (identifier, f"%{identifier}%"))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
            
        student_dict = dict(student)
        rollno = student_dict['rollno']
            
        sem_query = "SELECT semester, gpa FROM semester_marks WHERE rollno=? ORDER BY semester"
        cursor.execute(sem_query, (rollno,))
        semesters = cursor.fetchall()
        
        student_dict['semesters'] = [dict(sem) for sem in semesters]
        return jsonify(student_dict)
    finally:
        conn.close()

@app.route('/students', methods=['GET'])
def get_all_students():
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Cast to integer for sorting
        query = "SELECT rollno, name, email, department, current_cgpa, backlogs, placed FROM students ORDER BY CAST(rollno AS INTEGER) ASC"
        cursor.execute(query)
        students = cursor.fetchall()
        return jsonify([dict(student) for student in students])
    finally:
        conn.close()

@app.route('/student/<identifier>', methods=['DELETE'])
def delete_student(identifier):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM students WHERE rollno = ?", (identifier,))
        conn.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404
            
        return jsonify({"message": "Student deleted successfully"}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
