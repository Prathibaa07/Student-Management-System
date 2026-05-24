from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from decimal import Decimal

app = Flask(__name__)
CORS(app)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Prathi@07",
    database="studentdb"
)

@app.route('/student', methods=['POST'])
def add_student():
    try:
        db.ping(reconnect=True, attempts=3, delay=1)
    except Exception as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

    cursor = db.cursor()
    try:
        data = request.json
        for key in data:
            if data[key] == "":
                data[key] = None
        
        query = """
            INSERT INTO students (rollno, name, department, email, tenth_marks, twelfth_marks, current_cgpa, backlogs, placed, company_name)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            name=VALUES(name), department=VALUES(department), email=VALUES(email), tenth_marks=VALUES(tenth_marks),
            twelfth_marks=VALUES(twelfth_marks), current_cgpa=VALUES(current_cgpa), backlogs=VALUES(backlogs), 
            placed=VALUES(placed), company_name=VALUES(company_name)
        """
        values = (data['rollno'], data['name'], data.get('department'), data.get('email'), data.get('tenth_marks'), 
                  data.get('twelfth_marks'), data['current_cgpa'], data.get('backlogs', 0), data.get('placed', 'No'), data.get('company_name'))
        cursor.execute(query, values)
        
        if 'semesters' in data:
            cursor.execute("DELETE FROM semester_marks WHERE rollno=%s", (data['rollno'],))
            sem_query = "INSERT INTO semester_marks (rollno, semester, gpa) VALUES (%s, %s, %s)"
            sem_values = [(data['rollno'], sem['semester'], sem['gpa']) for sem in data['semesters']]
            cursor.executemany(sem_query, sem_values)
            
        db.commit()
        return jsonify({"message": "Student data saved successfully!"}), 201
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()

@app.route('/student/<identifier>', methods=['GET'])
def get_student(identifier):
    try:
        db.ping(reconnect=True, attempts=3, delay=1)
    except Exception as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

    cursor = db.cursor(dictionary=True)
    try:
        query = "SELECT * FROM students WHERE rollno=%s OR name LIKE %s"
        cursor.execute(query, (identifier, f"%{identifier}%"))
        student = cursor.fetchone()
        
        if not student:
            return jsonify({"error": "Student not found"}), 404
            
        rollno = student['rollno']
            
        sem_query = "SELECT semester, gpa FROM semester_marks WHERE rollno=%s ORDER BY semester"
        cursor.execute(sem_query, (rollno,))
        student['semesters'] = cursor.fetchall()
        
        for key, value in student.items():
            if isinstance(value, Decimal):
                student[key] = float(value)
                
        for sem in student['semesters']:
            if isinstance(sem['gpa'], Decimal):
                sem['gpa'] = float(sem['gpa'])
        
        return jsonify(student)
    finally:
        cursor.close()

@app.route('/students', methods=['GET'])
def get_all_students():
    try:
        db.ping(reconnect=True, attempts=3, delay=1)
    except Exception as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

    cursor = db.cursor(dictionary=True)
    try:
        query = "SELECT rollno, name, email, department, current_cgpa, backlogs, placed FROM students ORDER BY CAST(rollno AS UNSIGNED) ASC"
        cursor.execute(query)
        students = cursor.fetchall()
        
        for student in students:
            for key, value in student.items():
                if isinstance(value, Decimal):
                    student[key] = float(value)
                    
        return jsonify(students)
    finally:
        cursor.close()

@app.route('/student/<identifier>', methods=['DELETE'])
def delete_student(identifier):
    try:
        db.ping(reconnect=True, attempts=3, delay=1)
    except Exception as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

    cursor = db.cursor()
    try:
        query = "DELETE FROM students WHERE rollno = %s"
        cursor.execute(query, (identifier,))
        db.commit()
        
        if cursor.rowcount == 0:
            return jsonify({"error": "Student not found"}), 404
            
        return jsonify({"message": "Student deleted successfully"}), 200
    except Exception as e:
        db.rollback()
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
