-- School Management System Database Setup
-- Run this script on a new device to create the database and all required tables
-- Prerequisites: MySQL server installed and running, user with CREATE DATABASE privileges

-- Create database if it doesn't exist
CREATE DATABASE IF NOT EXISTS school_management;
USE school_management;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'principal', 'teacher', 'student', 'system_admin', 'academic_coordinator', 'admission_department') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Teachers table
CREATE TABLE IF NOT EXISTS teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    name VARCHAR(100) NOT NULL,
    age INT,
    dob DATE,
    highest_qualifications TEXT,
    teaching_subject VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Teaching records table
CREATE TABLE IF NOT EXISTS teaching_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT,
    school_name VARCHAR(255),
    duration VARCHAR(100),
    position VARCHAR(100),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
);

-- Classes table
CREATE TABLE IF NOT EXISTS classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    section VARCHAR(10) NOT NULL,
    UNIQUE KEY unique_class_section (class_name, section)
);

-- Subjects table
CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    class_id INT,
    teacher_id INT,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    admission_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    age INT,
    dob DATE,
    class_id INT,
    previous_school TEXT,
    father_name VARCHAR(100),
    mother_name VARCHAR(100),
    father_occupation VARCHAR(100),
    mother_occupation VARCHAR(100),
    contact_number VARCHAR(15),
    emergency_contact VARCHAR(15),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL
);

-- Student subjects table
CREATE TABLE IF NOT EXISTS student_subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    subject_id INT,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
);

-- Timetable table (with migration columns)
CREATE TABLE IF NOT EXISTS timetable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT,
    day_of_week VARCHAR(15),
    lecture_number INT,
    start_time TIME,
    end_time TIME,
    subject_id INT,
    teacher_id INT,
    break_start_time TIME,
    break_end_time TIME,
    created_by INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Student attendance table
CREATE TABLE IF NOT EXISTS student_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    date DATE NOT NULL,
    status ENUM('present', 'absent') NOT NULL,
    recorded_by INT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES teachers(id) ON DELETE CASCADE
);

-- Teacher attendance table
CREATE TABLE IF NOT EXISTS teacher_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT,
    date DATE NOT NULL,
    status ENUM('present', 'absent') NOT NULL,
    recorded_by INT,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES users(id) ON DELETE CASCADE
);

-- Teacher privileges table
CREATE TABLE IF NOT EXISTS teacher_privileges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT,
    can_edit_students BOOLEAN DEFAULT FALSE,
    can_delete_students BOOLEAN DEFAULT FALSE,
    can_suspend_students BOOLEAN DEFAULT FALSE,
    can_edit_subjects BOOLEAN DEFAULT FALSE,
    can_delete_subjects BOOLEAN DEFAULT FALSE,
    can_edit_attendance BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
);

-- Student status table
CREATE TABLE IF NOT EXISTS student_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    status ENUM('active', 'suspended', 'removed') DEFAULT 'active',
    suspension_reason TEXT,
    suspended_by INT,
    suspended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (suspended_by) REFERENCES users(id) ON DELETE SET NULL
);

-- Teacher status table
CREATE TABLE IF NOT EXISTS teacher_status (
     id INT AUTO_INCREMENT PRIMARY KEY,
     teacher_id INT,
     status ENUM('active', 'suspended', 'removed') DEFAULT 'active',
     suspension_reason TEXT,
     suspended_by INT,
     suspended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
     FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
     FOREIGN KEY (suspended_by) REFERENCES users(id) ON DELETE SET NULL
 );

-- Teacher assignments table
CREATE TABLE IF NOT EXISTS teacher_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT,
    class_id INT,
    subject_id INT,
    assigned_by INT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE KEY unique_teacher_class_subject (teacher_id, class_id, subject_id)
);

-- Create default admin user
-- Password is SHA256 hash of 'admin123'
INSERT IGNORE INTO users (username, password, role) VALUES
('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin');

-- Optional: Create sample data for testing (uncomment if needed)
-- INSERT INTO classes (class_name, section) VALUES ('10th', 'A'), ('10th', 'B'), ('9th', 'A');

COMMIT;
