CREATE DATABASE IF NOT EXISTS studentdb;

USE studentdb;

DROP TABLE IF EXISTS semester_marks;
DROP TABLE IF EXISTS students;

CREATE TABLE students (
    rollno VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department VARCHAR(50),
    email VARCHAR(100),
    tenth_marks DECIMAL(5, 2),
    twelfth_marks DECIMAL(5, 2),
    current_cgpa DECIMAL(4, 2) NOT NULL,
    backlogs INT DEFAULT 0,
    placed ENUM('Yes', 'No') DEFAULT 'No',
    company_name VARCHAR(100)
);

CREATE TABLE semester_marks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rollno VARCHAR(20),
    semester INT NOT NULL,
    gpa DECIMAL(4, 2) NOT NULL,
    FOREIGN KEY (rollno) REFERENCES students(rollno) ON DELETE CASCADE
);

INSERT INTO students (rollno, name, department, email, tenth_marks, twelfth_marks, current_cgpa, backlogs, placed, company_name) VALUES
('101', 'Alice Smith', 'Computer Science', 'alice@example.com', 92.5, 90.0, 8.5, 0, 'Yes', 'Google'),
('102', 'Bob Johnson', 'Mechanical', 'bob@example.com', 85.0, 82.0, 6.2, 2, 'No', NULL),
('103', 'Charlie Brown', 'Electrical', 'charlie@example.com', 95.0, 94.0, 9.1, 0, 'Yes', 'Microsoft'),
('104', 'David Lee', 'Civil', 'david@example.com', 78.0, 75.0, 7.4, 1, 'No', NULL);

INSERT INTO semester_marks (rollno, semester, gpa) VALUES
('101', 1, 8.0), ('101', 2, 8.2), ('101', 3, 8.6), ('101', 4, 8.8),
('102', 1, 6.5), ('102', 2, 6.0), ('102', 3, 5.8), ('102', 4, 6.5),
('103', 1, 9.0), ('103', 2, 9.1), ('103', 3, 9.2), ('103', 4, 9.1),
('104', 1, 7.5), ('104', 2, 7.2), ('104', 3, 7.4), ('104', 4, 7.5);
