-- COMPLETE MYSQL QUERIES FOR SCHOOL MANAGEMENT SYSTEM
-- This file contains ALL SQL statements used throughout the application
-- Organized by functionality for reference

-- =====================================================================================
-- DATABASE SETUP AND TABLE CREATION
-- =====================================================================================

-- Database creation
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

-- Timetable table
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

-- =====================================================================================
-- DATABASE MIGRATIONS AND FIXES
-- =====================================================================================

-- DATABASE UPDATE SCRIPT (also available as update_database.sql)
-- Run this to fix existing databases with missing columns

USE school_management;

-- Fix missing can_edit_attendance column in teacher_privileges table
-- Run this if you get "Unknown column 'tp.can_edit_attendance'" error
ALTER TABLE teacher_privileges ADD COLUMN can_edit_attendance BOOLEAN DEFAULT FALSE;

-- Verify the fix worked
SELECT 'Database update completed successfully!' as status;
DESCRIBE teacher_privileges;

-- =====================================================================================
-- DATABASE MIGRATIONS
-- =====================================================================================

-- Check if break_start_time column exists in timetable
SHOW COLUMNS FROM timetable LIKE 'break_start_time';

-- Add migration columns to timetable
ALTER TABLE timetable ADD COLUMN break_start_time TIME DEFAULT NULL;
ALTER TABLE timetable ADD COLUMN break_end_time TIME DEFAULT NULL;
ALTER TABLE timetable ADD COLUMN created_by INT DEFAULT NULL;
ALTER TABLE timetable ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE timetable ADD CONSTRAINT fk_timetable_created_by FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL;

-- =====================================================================================
-- USER AUTHENTICATION AND LOGIN
-- =====================================================================================

-- Login query
SELECT * FROM users WHERE username = %s AND password = %s;

-- Check teacher suspension status
SELECT status, suspension_reason FROM teacher_status WHERE teacher_id = (SELECT id FROM teachers WHERE user_id = %s);

-- =====================================================================================
-- DEFAULT DATA INSERTION
-- =====================================================================================

-- Create default admin user
INSERT INTO users (username, password, role) VALUES (%s, %s, 'admin');

-- =====================================================================================
-- TEACHER MANAGEMENT
-- =====================================================================================

-- Insert teacher user account
INSERT INTO users (username, password, role) VALUES (%s, %s, 'teacher');

-- Insert teacher profile
INSERT INTO teachers (user_id, name, age, dob, highest_qualifications, teaching_subject) VALUES (%s, %s, %s, %s, %s, %s);

-- Insert teaching records
INSERT INTO teaching_records (teacher_id, school_name, duration, position) VALUES (%s, %s, %s, %s);

-- =====================================================================================
-- PRINCIPAL MANAGEMENT
-- =====================================================================================

-- Insert principal user account
INSERT INTO users (username, password, role) VALUES (%s, %s, 'principal');

-- Insert principal profile (using teachers table)
INSERT INTO teachers (user_id, name, age, dob, highest_qualifications, teaching_subject) VALUES (%s, %s, %s, %s, %s, %s);

-- =====================================================================================
-- ACADEMIC COORDINATOR MANAGEMENT
-- =====================================================================================

-- Insert academic coordinator user account
INSERT INTO users (username, password, role) VALUES (%s, %s, 'academic_coordinator');

-- Insert academic coordinator profile
INSERT INTO teachers (user_id, name, age, dob, highest_qualifications, teaching_subject) VALUES (%s, %s, %s, %s, %s, %s);

-- =====================================================================================
-- ADMISSION DEPARTMENT MANAGEMENT
-- =====================================================================================

-- Insert admission department user account
INSERT INTO users (username, password, role) VALUES (%s, %s, 'admission_department');

-- Insert admission department profile
INSERT INTO teachers (user_id, name, age, dob, highest_qualifications, teaching_subject) VALUES (%s, %s, %s, %s, %s, %s);

-- =====================================================================================
-- CLASS MANAGEMENT
-- =====================================================================================

-- Create new class
INSERT INTO classes (class_name, section) VALUES (%s, %s);

-- =====================================================================================
-- SUBJECT MANAGEMENT
-- =====================================================================================

-- Create new subject
INSERT INTO subjects (subject_name, class_id, teacher_id) VALUES (%s, %s, %s);

-- Create teacher assignment record
INSERT INTO teacher_assignments (teacher_id, class_id, subject_id, assigned_by) VALUES (%s, %s, %s, %s);

-- =====================================================================================
-- STUDENT MANAGEMENT
-- =====================================================================================

-- Insert student user account
INSERT INTO users (username, password, role) VALUES (%s, %s, 'student');

-- Insert student profile
INSERT INTO students (user_id, admission_number, name, age, dob, class_id, previous_school, father_name, mother_name, father_occupation, mother_occupation, contact_number, emergency_contact) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);

-- Auto-assign subjects to student
INSERT INTO student_subjects (student_id, subject_id) VALUES (%s, %s);

-- =====================================================================================
-- TIMETABLE MANAGEMENT
-- =====================================================================================

-- Insert timetable entry
INSERT INTO timetable (class_id, day_of_week, lecture_number, start_time, end_time, subject_id, teacher_id, break_start_time, break_end_time, created_by) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);

-- =====================================================================================
-- ATTENDANCE MANAGEMENT
-- =====================================================================================

-- Mark student attendance (check existing)
SELECT id FROM student_attendance WHERE student_id = %s AND date = %s;

-- Insert new student attendance
INSERT INTO student_attendance (student_id, date, status, recorded_by) VALUES (%s, %s, %s, %s);

-- Update existing student attendance
UPDATE student_attendance SET status = %s, recorded_by = %s, recorded_at = CURRENT_TIMESTAMP WHERE id = %s;

-- Mark teacher attendance (check existing)
SELECT id FROM teacher_attendance WHERE teacher_id = %s AND date = %s;

-- Insert new teacher attendance
INSERT INTO teacher_attendance (teacher_id, date, status, recorded_by) VALUES (%s, %s, %s, %s);

-- Update existing teacher attendance
UPDATE teacher_attendance SET status = %s, recorded_by = %s, recorded_at = CURRENT_TIMESTAMP WHERE id = %s;

-- =====================================================================================
-- VIEW QUERIES (READ OPERATIONS)
-- =====================================================================================

-- View attendance records (student)
SELECT sa.date, s.name as student_name, c.class_name, c.section, sa.status, t.name as recorded_by FROM student_attendance sa JOIN students s ON sa.student_id = s.id JOIN classes c ON s.class_id = c.id JOIN teachers t ON sa.recorded_by = t.id ORDER BY sa.date DESC, s.name LIMIT 50;

-- View attendance records (teacher)
SELECT ta.date, t.name as teacher_name, ta.status, u.username as recorded_by, ta.recorded_at FROM teacher_attendance ta JOIN teachers t ON ta.teacher_id = t.id JOIN users u ON ta.recorded_by = u.id ORDER BY ta.date DESC, t.name LIMIT 50;

-- View all teachers
SELECT t.*, COUNT(tr.id) as record_count FROM teachers t LEFT JOIN teaching_records tr ON t.id = tr.teacher_id GROUP BY t.id ORDER BY t.name;

-- View all students by class and section
SELECT s.*, c.class_name, c.section FROM students s JOIN classes c ON s.class_id = c.id ORDER BY c.class_name, c.section, s.name;

-- View all classes with counts
SELECT c.*, COUNT(s.id) as student_count, COUNT(sub.id) as subject_count FROM classes c LEFT JOIN students s ON c.id = s.class_id LEFT JOIN subjects sub ON c.id = sub.class_id GROUP BY c.id ORDER BY c.class_name, c.section;

-- View teacher timetable
SELECT tt.day_of_week, tt.lecture_number, tt.start_time, tt.end_time, s.subject_name, c.class_name, c.section, tt.break_start_time, tt.break_end_time FROM timetable tt LEFT JOIN subjects s ON tt.subject_id = s.id JOIN classes c ON tt.class_id = c.id WHERE tt.teacher_id = (SELECT id FROM teachers WHERE user_id = %s) ORDER BY FIELD(tt.day_of_week, 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'), tt.lecture_number;

-- View teacher attendance
SELECT date, status, recorded_at FROM teacher_attendance WHERE teacher_id = (SELECT id FROM teachers WHERE user_id = %s) ORDER BY date DESC LIMIT 30;

-- View teacher's assigned students
SELECT DISTINCT s.id, s.name, s.admission_number, c.class_name, c.section, CASE WHEN ss.status IS NULL THEN 'active' ELSE ss.status END as status FROM students s JOIN classes c ON s.class_id = c.id JOIN teacher_assignments ta ON ta.class_id = c.id LEFT JOIN student_status ss ON s.id = ss.student_id LEFT JOIN student_subjects sts ON s.id = sts.student_id LEFT JOIN subjects sub ON sts.subject_id = sub.id WHERE ta.teacher_id = (SELECT id FROM teachers WHERE user_id = %s) ORDER BY c.class_name, c.section, s.name;

-- View student timetable
SELECT tt.day_of_week, tt.lecture_number, tt.start_time, tt.end_time, s.subject_name, t.name as teacher_name FROM timetable tt JOIN subjects s ON tt.subject_id = s.id JOIN teachers t ON tt.teacher_id = t.id WHERE tt.class_id = (SELECT class_id FROM students WHERE user_id = %s) ORDER BY FIELD(tt.day_of_week, 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'), tt.lecture_number;

-- View student attendance
SELECT date, status, recorded_at FROM student_attendance WHERE student_id = (SELECT id FROM students WHERE user_id = %s) ORDER BY date DESC LIMIT 30;

-- View student subjects
SELECT s.subject_name, t.name as teacher_name FROM subjects s JOIN teachers t ON s.teacher_id = t.id WHERE s.class_id = (SELECT class_id FROM students WHERE user_id = %s) ORDER BY s.subject_name;

-- View student attendance history
SELECT sa.date, sa.status, sa.recorded_at, CASE WHEN sa.recorded_by IS NOT NULL THEN t.name ELSE 'Admin' END as recorded_by_name FROM student_attendance sa LEFT JOIN teachers t ON sa.recorded_by = t.id WHERE sa.student_id = (SELECT id FROM students WHERE user_id = %s) ORDER BY sa.date DESC, sa.recorded_at DESC;

-- View student attendance history (admin)
SELECT sa.date, sa.status, sa.recorded_at, CASE WHEN sa.recorded_by IS NOT NULL THEN t.name ELSE 'Admin' END as recorded_by_name FROM student_attendance sa LEFT JOIN teachers t ON sa.recorded_by = t.id WHERE sa.student_id = %s ORDER BY sa.date DESC, sa.recorded_at DESC;

-- View student profile
SELECT s.*, c.class_name, c.section FROM students s JOIN classes c ON s.class_id = c.id WHERE s.user_id = %s;

-- View teacher profile
SELECT t.*, u.username, COUNT(tr.id) as record_count, tp.* FROM teachers t JOIN users u ON t.user_id = u.id LEFT JOIN teaching_records tr ON t.id = tr.teacher_id LEFT JOIN teacher_privileges tp ON t.id = tp.teacher_id WHERE t.user_id = %s GROUP BY t.id;

-- View teacher assigned classes
SELECT DISTINCT c.class_name, c.section, COUNT(DISTINCT s.id) as student_count, COUNT(DISTINCT sub.id) as subject_count FROM teacher_assignments ta JOIN classes c ON ta.class_id = c.id LEFT JOIN students s ON c.id = s.class_id LEFT JOIN student_status ss ON s.id = ss.student_id AND ss.status = 'removed' LEFT JOIN subjects sub ON ta.subject_id = sub.id WHERE ta.teacher_id = (SELECT id FROM teachers WHERE user_id = %s) AND ss.id IS NULL GROUP BY c.class_name, c.section ORDER BY c.class_name, c.section;

-- View all subjects
SELECT s.id, s.subject_name, c.class_name, c.section, t.name as teacher_name FROM subjects s JOIN classes c ON s.class_id = c.id LEFT JOIN teachers t ON s.teacher_id = t.id ORDER BY c.class_name, c.section, s.subject_name;

-- View student attendance history (specific student)
SELECT sa.date, sa.status, sa.recorded_at, CASE WHEN sa.recorded_by IS NOT NULL THEN t.name ELSE 'Admin' END as recorded_by_name FROM student_attendance sa LEFT JOIN teachers t ON sa.recorded_by = t.id WHERE sa.student_id = %s ORDER BY sa.date DESC, sa.recorded_at DESC;

-- =====================================================================================
-- TEACHER PRIVILEGES MANAGEMENT
-- =====================================================================================

-- View teacher privileges
SELECT t.id, t.name, tp.* FROM teachers t LEFT JOIN teacher_privileges tp ON t.id = tp.teacher_id ORDER BY t.name;

-- Check teacher privileges
SELECT * FROM teacher_privileges WHERE teacher_id = (SELECT id FROM teachers WHERE user_id = %s);

-- Insert teacher privileges
INSERT INTO teacher_privileges (teacher_id, can_edit_students, can_delete_students, can_suspend_students, can_edit_subjects, can_delete_subjects, can_edit_attendance) VALUES (%s, %s, %s, %s, %s, %s, %s);

-- Update teacher privileges
UPDATE teacher_privileges SET can_edit_students = %s, can_delete_students = %s, can_suspend_students = %s, can_edit_subjects = %s, can_delete_subjects = %s, can_edit_attendance = %s WHERE teacher_id = %s;

-- =====================================================================================
-- STUDENT STATUS MANAGEMENT
-- =====================================================================================

-- View active students for suspension
SELECT s.id, s.name, s.admission_number, c.class_name, c.section FROM students s JOIN classes c ON s.class_id = c.id LEFT JOIN student_status ss ON s.id = ss.student_id WHERE ss.status IS NULL OR ss.status = 'active' ORDER BY c.class_name, c.section, s.name;

-- Suspend student
INSERT INTO student_status (student_id, status, suspension_reason, suspended_by) VALUES (%s, 'suspended', %s, %s) ON DUPLICATE KEY UPDATE status = 'suspended', suspension_reason = %s, suspended_by = %s, suspended_at = CURRENT_TIMESTAMP;

-- View suspended students
SELECT s.id, s.name, s.admission_number, c.class_name, c.section, ss.suspension_reason FROM students s JOIN classes c ON s.class_id = c.id JOIN student_status ss ON s.id = ss.student_id WHERE ss.status = 'suspended' ORDER BY c.class_name, c.section, s.name;

-- Unsuspend student
UPDATE student_status SET status = 'active', suspension_reason = NULL WHERE student_id = %s;

-- View students available for removal
SELECT s.id, s.name, s.admission_number, c.class_name, c.section FROM students s JOIN classes c ON s.class_id = c.id LEFT JOIN student_status ss ON s.id = ss.student_id WHERE ss.status IS NULL OR ss.status != 'removed' ORDER BY c.class_name, c.section, s.name;

-- Remove student
INSERT INTO student_status (student_id, status, suspension_reason, suspended_by) VALUES (%s, 'removed', 'Administrative removal', %s) ON DUPLICATE KEY UPDATE status = 'removed', suspension_reason = 'Administrative removal', suspended_by = %s, suspended_at = CURRENT_TIMESTAMP;

-- View suspended students (summary)
SELECT s.name, s.admission_number, c.class_name, c.section, ss.suspension_reason, ss.suspended_at, u.username as suspended_by FROM students s JOIN classes c ON s.class_id = c.id JOIN student_status ss ON s.id = ss.student_id LEFT JOIN users u ON ss.suspended_by = u.id WHERE ss.status = 'suspended' ORDER BY ss.suspended_at DESC;

-- View removed students
SELECT s.name, s.admission_number, c.class_name, c.section, ss.suspended_at, u.username as removed_by FROM students s JOIN classes c ON s.class_id = c.id JOIN student_status ss ON s.id = ss.student_id LEFT JOIN users u ON ss.suspended_by = u.id WHERE ss.status = 'removed' ORDER BY ss.suspended_at DESC;

-- =====================================================================================
-- TEACHER STATUS MANAGEMENT
-- =====================================================================================

-- View active teachers for suspension
SELECT t.id, t.name, t.teaching_subject FROM teachers t LEFT JOIN teacher_status ts ON t.id = ts.teacher_id WHERE ts.status IS NULL OR ts.status = 'active' ORDER BY t.name;

-- Suspend teacher
INSERT INTO teacher_status (teacher_id, status, suspension_reason, suspended_by) VALUES (%s, 'suspended', %s, %s) ON DUPLICATE KEY UPDATE status = 'suspended', suspension_reason = %s, suspended_by = %s, suspended_at = CURRENT_TIMESTAMP;

-- View suspended teachers
SELECT t.id, t.name, t.teaching_subject, ts.suspension_reason FROM teachers t JOIN teacher_status ts ON t.id = ts.teacher_id WHERE ts.status = 'suspended' ORDER BY t.name;

-- Unsuspend teacher
UPDATE teacher_status SET status = 'active', suspension_reason = NULL WHERE teacher_id = %s;

-- View teachers available for removal
SELECT t.id, t.name, t.teaching_subject FROM teachers t LEFT JOIN teacher_status ts ON t.id = ts.teacher_id WHERE ts.status IS NULL OR ts.status != 'removed' ORDER BY t.name;

-- Remove teacher
INSERT INTO teacher_status (teacher_id, status, suspension_reason, suspended_by) VALUES (%s, 'removed', 'Administrative removal', %s) ON DUPLICATE KEY UPDATE status = 'removed', suspension_reason = 'Administrative removal', suspended_by = %s, suspended_at = CURRENT_TIMESTAMP;

-- View suspended teachers (summary)
SELECT t.name, t.teaching_subject, ts.suspension_reason, ts.suspended_at, u.username as suspended_by FROM teachers t JOIN teacher_status ts ON t.id = ts.teacher_id LEFT JOIN users u ON ts.suspended_by = u.id WHERE ts.status = 'suspended' ORDER BY ts.suspended_at DESC;

-- View removed teachers
SELECT t.name, t.teaching_subject, ts.suspended_at, u.username as removed_by FROM teachers t JOIN teacher_status ts ON t.id = ts.teacher_id LEFT JOIN users u ON ts.suspended_by = u.id WHERE ts.status = 'removed' ORDER BY ts.suspended_at DESC;

-- =====================================================================================
-- SUBJECT ALLOTMENT AND ASSIGNMENT
-- =====================================================================================

-- Allot subjects to student (clear existing)
DELETE FROM student_subjects WHERE student_id = %s;

-- Allot subjects to student (add new)
INSERT INTO student_subjects (student_id, subject_id) VALUES (%s, %s);

-- View student's current subjects
SELECT ss.id, s.subject_name, s.id as subject_id FROM student_subjects ss JOIN subjects s ON ss.subject_id = s.id WHERE ss.student_id = %s ORDER BY s.subject_name;

-- View available subjects for class
SELECT s.id, s.subject_name, t.name as teacher_name FROM subjects s LEFT JOIN teachers t ON s.teacher_id = t.id WHERE s.class_id = (SELECT class_id FROM students WHERE id = %s) ORDER BY s.subject_name;

-- =====================================================================================
-- CLASS AND SUBJECT MANAGEMENT
-- =====================================================================================

-- View available classes
SELECT * FROM classes ORDER BY class_name, section;

-- View available teachers
SELECT * FROM teachers ORDER BY name;

-- Verify class exists
SELECT class_name, section FROM classes WHERE id = %s;

-- Verify teacher exists
SELECT name FROM teachers WHERE id = %s;

-- View subjects for class
SELECT id, subject_name FROM subjects WHERE class_id = %s ORDER BY subject_name;

-- Verify subject exists for class
SELECT s.subject_name, s.teacher_id, t.name as teacher_name FROM subjects s LEFT JOIN teachers t ON s.teacher_id = t.id WHERE s.id = %s AND s.class_id = %s;

-- =====================================================================================
-- TEACHER ASSIGNMENT MANAGEMENT
-- =====================================================================================

-- View teachers with assignment counts
SELECT t.id, t.name, COUNT(ta.id) as assignment_count FROM teachers t LEFT JOIN teacher_assignments ta ON t.id = ta.teacher_id GROUP BY t.id, t.name ORDER BY t.name;

-- View current assignments for teacher
SELECT ta.id, c.class_name, c.section, s.subject_name, ta.assigned_at FROM teacher_assignments ta JOIN classes c ON ta.class_id = c.id JOIN subjects s ON ta.subject_id = s.id WHERE ta.teacher_id = %s ORDER BY c.class_name, c.section, s.subject_name;

-- Check if assignment exists
SELECT id FROM teacher_assignments WHERE teacher_id = %s AND class_id = %s AND subject_id = %s;

-- Create teacher assignment
INSERT INTO teacher_assignments (teacher_id, class_id, subject_id, assigned_by) VALUES (%s, %s, %s, %s);

-- Update subject teacher
UPDATE subjects SET teacher_id = %s WHERE id = %s;

-- Remove teacher assignment
DELETE FROM teacher_assignments WHERE id = %s;

-- Check if teacher has other assignments for subject
SELECT id FROM teacher_assignments WHERE teacher_id = %s AND subject_id = %s;

-- Remove teacher from subject if no other assignments
UPDATE subjects SET teacher_id = NULL WHERE id = %s;

-- =====================================================================================
-- STUDENT CLASS ASSIGNMENT EDITING
-- =====================================================================================

-- View all students for reassignment
SELECT s.id, s.name, s.admission_number, c.class_name, c.section, CASE WHEN ss.status IS NULL THEN 'active' ELSE ss.status END as status FROM students s JOIN classes c ON s.class_id = c.id LEFT JOIN student_status ss ON s.id = ss.student_id ORDER BY c.class_name, c.section, s.name;

-- View distinct class names
SELECT DISTINCT class_name FROM classes ORDER BY class_name;

-- View sections for class
SELECT id, section FROM classes WHERE class_name = %s ORDER BY section;

-- Verify class-section combination
SELECT id, class_name, section FROM classes WHERE id = %s;

-- Update student class
UPDATE students SET class_id = %s WHERE id = %s;

-- Remove old subject assignments
DELETE FROM student_subjects WHERE student_id = %s;

-- Get subjects for new class
SELECT id, subject_name FROM subjects WHERE class_id = %s;

-- Add new subject assignments
INSERT INTO student_subjects (student_id, subject_id) VALUES (%s, %s);

-- =====================================================================================
-- SUBJECT MANAGEMENT (DELETE)
-- =====================================================================================

-- Delete subject
DELETE FROM subjects WHERE id = %s;

-- =====================================================================================
-- PRINCIPAL VIEW QUERIES
-- =====================================================================================

-- View all timetables
SELECT tt.day_of_week, tt.lecture_number, tt.start_time, tt.end_time, s.subject_name, c.class_name, c.section, t.name as teacher_name FROM timetable tt JOIN subjects s ON tt.subject_id = s.id JOIN classes c ON tt.class_id = c.id JOIN teachers t ON tt.teacher_id = t.id ORDER BY FIELD(tt.day_of_week, 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'), tt.lecture_number, c.class_name, c.section;

-- View teacher assignments
SELECT t.name, ta.class_id, c.class_name, c.section, s.subject_name FROM teacher_assignments ta JOIN teachers t ON ta.teacher_id = t.id JOIN classes c ON ta.class_id = c.id JOIN subjects s ON ta.subject_id = s.id ORDER BY t.name, c.class_name, c.section;

-- View student status summary
SELECT c.class_name, c.section, COUNT(s.id) as total_students, SUM(CASE WHEN ss.status IS NULL OR ss.status = 'active' THEN 1 ELSE 0 END) as active_students, SUM(CASE WHEN ss.status = 'suspended' THEN 1 ELSE 0 END) as suspended_students, SUM(CASE WHEN ss.status = 'removed' THEN 1 ELSE 0 END) as removed_students FROM classes c LEFT JOIN students s ON c.id = s.class_id LEFT JOIN student_status ss ON s.id = ss.student_id GROUP BY c.class_name, c.section ORDER BY c.class_name, c.section;

-- =====================================================================================
-- DATABASE MAINTENANCE
-- =====================================================================================

-- Clear teacher privileges
DELETE FROM teacher_privileges;

-- Clear teacher assignments
DELETE FROM teacher_assignments;

-- Clear teaching records
DELETE FROM teaching_records;

-- Clear teacher attendance
DELETE FROM teacher_attendance;

-- Clear timetable entries for teachers
DELETE ta FROM timetable ta JOIN subjects s ON ta.subject_id = s.id WHERE s.teacher_id IS NOT NULL;

-- Remove teacher from subjects
UPDATE subjects SET teacher_id = NULL;

-- Clear teachers
DELETE FROM teachers;

-- Clear teacher users
DELETE FROM users WHERE role = 'teacher';

-- Clear student status
DELETE FROM student_status;

-- Clear student subjects
DELETE FROM student_subjects;

-- Clear student attendance
DELETE FROM student_attendance;

-- Clear teachers (for student clearance)
DELETE FROM teachers;

-- Clear students
DELETE FROM students;

-- Clear student users
DELETE FROM users WHERE role = 'student';

-- Clear classes
DELETE FROM teacher_assignments;
DELETE FROM student_subjects;
DELETE FROM subjects;
DELETE FROM timetable;
DELETE FROM classes;

-- Clear subjects
DELETE FROM student_subjects;
DELETE FROM teacher_assignments;
DELETE FROM timetable;
DELETE FROM subjects;

-- Clear timetables
DELETE FROM timetable;

-- Clear attendance records
DELETE FROM student_attendance;
DELETE FROM teacher_attendance;

-- Clear assignments and privileges
DELETE FROM teacher_privileges;
DELETE FROM teacher_assignments;

-- Complete database reset
DELETE FROM teacher_privileges;
DELETE FROM teacher_assignments;
DELETE FROM student_status;
DELETE FROM student_subjects;
DELETE FROM teaching_records;
DELETE FROM timetable;
DELETE FROM student_attendance;
DELETE FROM teacher_attendance;
DELETE FROM subjects;
DELETE FROM students;
DELETE FROM teachers;
DELETE FROM classes;
DELETE FROM users WHERE role != 'admin';

COMMIT;
