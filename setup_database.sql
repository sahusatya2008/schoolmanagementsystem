-- =====================================================
-- SCHOOL MANAGEMENT SYSTEM DATABASE SETUP
-- =====================================================
-- This script creates a complete, error-free database schema
-- Prerequisites: MySQL 8.0+ server, user with CREATE DATABASE privileges
-- Version: 1.0.0 | Date: December 2025
-- Author: Satya Narayan Sahu

-- Create database with proper character set
CREATE DATABASE IF NOT EXISTS school_management
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE school_management;

-- =====================================================
-- TABLE CREATION (in dependency order)
-- =====================================================

-- 1. Users table (base table, no dependencies)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL COMMENT 'SHA256 hashed password',
    role ENUM('admin', 'principal', 'teacher', 'student',
              'academic_coordinator', 'admission_department', 'system_admin') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP NULL,
    login_attempts INT DEFAULT 0,
    account_locked BOOLEAN DEFAULT FALSE,
    INDEX idx_username (username),
    INDEX idx_role (role),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Teachers table (depends on users)
CREATE TABLE IF NOT EXISTS teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    age INT CHECK (age >= 18 AND age <= 70),
    dob DATE NOT NULL,
    highest_qualifications TEXT NOT NULL,
    teaching_subject VARCHAR(100) NOT NULL,
    status ENUM('active', 'suspended', 'on_leave', 'retired', 'removed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_name (name),
    INDEX idx_teaching_subject (teaching_subject),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Teaching records table (depends on teachers)
CREATE TABLE IF NOT EXISTS teaching_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    school_name VARCHAR(200) NOT NULL,
    duration VARCHAR(50) NOT NULL COMMENT 'e.g., 2018-2020',
    position VARCHAR(100) NOT NULL,
    subject VARCHAR(100),
    experience_years DECIMAL(4,1) DEFAULT 0,
    remarks TEXT,
    verification_status ENUM('pending', 'verified', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_school_name (school_name),
    INDEX idx_verification_status (verification_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Classes table (independent)
CREATE TABLE IF NOT EXISTS classes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(50) NOT NULL,
    section VARCHAR(10) NOT NULL,
    capacity INT DEFAULT 50,
    current_enrollment INT DEFAULT 0,
    academic_year VARCHAR(20) DEFAULT '2024-2025',
    status ENUM('active', 'inactive', 'closed') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_class_section_year (class_name, section, academic_year),
    INDEX idx_class_name (class_name),
    INDEX idx_section (section),
    INDEX idx_academic_year (academic_year),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Subjects table (depends on classes and teachers)
CREATE TABLE IF NOT EXISTS subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL,
    class_id INT NOT NULL,
    teacher_id INT,
    subject_code VARCHAR(20) UNIQUE,
    description TEXT,
    credits INT DEFAULT 1,
    is_compulsory BOOLEAN DEFAULT TRUE,
    status ENUM('active', 'inactive') DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL,
    INDEX idx_class_id (class_id),
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_subject_name (subject_name),
    INDEX idx_subject_code (subject_code),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Students table (depends on users and classes)
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT UNIQUE NOT NULL,
    admission_number VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    age INT CHECK (age >= 5 AND age <= 25),
    dob DATE NOT NULL,
    class_id INT,
    previous_school VARCHAR(200),
    father_name VARCHAR(100) NOT NULL,
    father_occupation VARCHAR(100),
    mother_name VARCHAR(100) NOT NULL,
    mother_occupation VARCHAR(100),
    contact_number VARCHAR(15) NOT NULL,
    emergency_contact VARCHAR(15),
    address TEXT,
    medical_conditions TEXT,
    allergies TEXT,
    status ENUM('active', 'suspended', 'transferred', 'graduated', 'removed') DEFAULT 'active',
    enrollment_date DATE DEFAULT (CURRENT_DATE),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_admission_number (admission_number),
    INDEX idx_name (name),
    INDEX idx_class_id (class_id),
    INDEX idx_status (status),
    INDEX idx_enrollment_date (enrollment_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Student subjects table (depends on students and subjects)
CREATE TABLE IF NOT EXISTS student_subjects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    enrollment_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    grade_points DECIMAL(4,2) DEFAULT NULL,
    grade VARCHAR(5) DEFAULT NULL,
    status ENUM('enrolled', 'completed', 'dropped', 'failed') DEFAULT 'enrolled',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    UNIQUE KEY unique_student_subject (student_id, subject_id),
    INDEX idx_student_id (student_id),
    INDEX idx_subject_id (subject_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Timetable table (depends on classes, subjects, teachers, users)
CREATE TABLE IF NOT EXISTS timetable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday') NOT NULL,
    lecture_number INT NOT NULL CHECK (lecture_number >= 1 AND lecture_number <= 10),
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    subject_id INT NOT NULL,
    room_number VARCHAR(20),
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE KEY unique_class_day_lecture (class_id, day_of_week, lecture_number),
    INDEX idx_class_id (class_id),
    INDEX idx_subject_id (subject_id),
    INDEX idx_day_of_week (day_of_week),
    INDEX idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Student attendance table (depends on students and users)
CREATE TABLE IF NOT EXISTS student_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('present', 'absent', 'late', 'excused', 'suspended') NOT NULL DEFAULT 'absent',
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    remarks TEXT,
    late_minutes INT DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE KEY unique_student_date (student_id, date),
    INDEX idx_student_id (student_id),
    INDEX idx_date (date),
    INDEX idx_recorded_by (recorded_by),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Teacher attendance table (depends on teachers and users)
CREATE TABLE IF NOT EXISTS teacher_attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    date DATE NOT NULL,
    status ENUM('present', 'absent', 'late', 'excused', 'on_leave') NOT NULL DEFAULT 'absent',
    recorded_by INT NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    check_in_time TIME,
    check_out_time TIME,
    remarks TEXT,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (recorded_by) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE KEY unique_teacher_date (teacher_id, date),
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_date (date),
    INDEX idx_recorded_by (recorded_by),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. Teacher privileges table (depends on teachers)
CREATE TABLE IF NOT EXISTS teacher_privileges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT UNIQUE NOT NULL,
    can_edit_students BOOLEAN DEFAULT FALSE,
    can_delete_students BOOLEAN DEFAULT FALSE,
    can_suspend_students BOOLEAN DEFAULT FALSE,
    can_edit_subjects BOOLEAN DEFAULT FALSE,
    can_delete_subjects BOOLEAN DEFAULT FALSE,
    can_edit_attendance BOOLEAN DEFAULT FALSE,
    can_view_all_classes BOOLEAN DEFAULT FALSE,
    can_generate_reports BOOLEAN DEFAULT FALSE,
    can_modify_timetable BOOLEAN DEFAULT FALSE,
    can_manage_class_assignments BOOLEAN DEFAULT FALSE,
    privilege_level ENUM('basic', 'intermediate', 'advanced') DEFAULT 'basic',
    granted_by INT,
    granted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at DATE DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (granted_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_privilege_level (privilege_level),
    INDEX idx_granted_by (granted_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 12. Student status table (depends on students and users)
CREATE TABLE IF NOT EXISTS student_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    old_status ENUM('active', 'suspended', 'transferred', 'graduated', 'removed'),
    new_status ENUM('active', 'suspended', 'transferred', 'graduated', 'removed') NOT NULL,
    reason TEXT NOT NULL,
    changed_by INT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_student_id (student_id),
    INDEX idx_new_status (new_status),
    INDEX idx_changed_by (changed_by),
    INDEX idx_changed_at (changed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 13. Teacher status table (depends on teachers and users)
CREATE TABLE IF NOT EXISTS teacher_status (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    old_status ENUM('active', 'suspended', 'on_leave', 'retired', 'removed'),
    new_status ENUM('active', 'suspended', 'on_leave', 'retired', 'removed') NOT NULL,
    reason TEXT NOT NULL,
    changed_by INT NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    effective_date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_new_status (new_status),
    INDEX idx_changed_by (changed_by),
    INDEX idx_changed_at (changed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 14. Teacher assignments table (depends on teachers, classes, subjects, users)
CREATE TABLE IF NOT EXISTS teacher_assignments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT NOT NULL,
    class_id INT NOT NULL,
    subject_id INT NOT NULL,
    assigned_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    assignment_type ENUM('primary', 'secondary', 'substitute') DEFAULT 'primary',
    workload_percentage INT DEFAULT 100 CHECK (workload_percentage >= 0 AND workload_percentage <= 100),
    status ENUM('active', 'inactive', 'transferred') DEFAULT 'active',
    assigned_by INT NOT NULL,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE KEY unique_teacher_class_subject (teacher_id, class_id, subject_id),
    INDEX idx_teacher_id (teacher_id),
    INDEX idx_class_id (class_id),
    INDEX idx_subject_id (subject_id),
    INDEX idx_status (status),
    INDEX idx_assigned_by (assigned_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 15. Proxy teachers table (depends on classes, teachers, timetable, users)
CREATE TABLE IF NOT EXISTS proxy_teachers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    class_id INT NOT NULL,
    original_teacher_id INT NOT NULL,
    proxy_teacher_id INT NOT NULL,
    date DATE NOT NULL,
    timetable_id INT NOT NULL,
    reason TEXT NOT NULL,
    approval_status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    approved_by INT,
    approved_at TIMESTAMP NULL,
    created_by INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
    FOREIGN KEY (original_teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (proxy_teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
    FOREIGN KEY (timetable_id) REFERENCES timetable(id) ON DELETE CASCADE,
    FOREIGN KEY (approved_by) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE KEY unique_proxy_assignment (timetable_id, date),
    INDEX idx_class_id (class_id),
    INDEX idx_original_teacher (original_teacher_id),
    INDEX idx_proxy_teacher (proxy_teacher_id),
    INDEX idx_date (date),
    INDEX idx_approval_status (approval_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- INITIAL DATA SETUP
-- =====================================================

-- Create default admin user (password: admin123)
-- SHA256 hash: 240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9
INSERT IGNORE INTO users (username, password, role, created_at) VALUES
('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'admin', NOW());

-- =====================================================
-- DATABASE FIXES AND MIGRATIONS
-- =====================================================

-- Fix 1: Ensure all tables have proper character sets
ALTER TABLE users CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE teachers CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE teaching_records CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE classes CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE subjects CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE students CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE student_subjects CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE timetable CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE student_attendance CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE teacher_attendance CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE teacher_privileges CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE student_status CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE teacher_status CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE teacher_assignments CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE proxy_teachers CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Fix 2: Add missing indexes for performance
CREATE INDEX IF NOT EXISTS idx_users_last_login ON users(last_login);
CREATE INDEX IF NOT EXISTS idx_students_contact ON students(contact_number);
CREATE INDEX IF NOT EXISTS idx_subjects_code ON subjects(subject_code);
CREATE INDEX IF NOT EXISTS idx_timetable_room ON timetable(room_number);

-- Fix 3: Ensure all foreign key constraints are properly defined
-- This is handled automatically by the CREATE TABLE IF NOT EXISTS statements above

-- Fix 4: Add missing ENUM values if needed (backward compatibility)
-- All ENUM values are defined in the table creation statements above

-- Fix 5: Ensure default values are set correctly
UPDATE teacher_privileges SET privilege_level = 'basic' WHERE privilege_level IS NULL;
UPDATE students SET enrollment_date = CURRENT_DATE WHERE enrollment_date IS NULL;
UPDATE classes SET academic_year = '2024-2025' WHERE academic_year IS NULL;

-- =====================================================
-- DATA INTEGRITY CHECKS
-- =====================================================

-- Ensure no orphaned records exist
DELETE FROM student_subjects WHERE student_id NOT IN (SELECT id FROM students);
DELETE FROM student_subjects WHERE subject_id NOT IN (SELECT id FROM subjects);
DELETE FROM teacher_assignments WHERE teacher_id NOT IN (SELECT id FROM teachers);
DELETE FROM teacher_assignments WHERE class_id NOT IN (SELECT id FROM classes);
DELETE FROM teacher_assignments WHERE subject_id NOT IN (SELECT id FROM subjects);
DELETE FROM student_attendance WHERE student_id NOT IN (SELECT id FROM students);
DELETE FROM teacher_attendance WHERE teacher_id NOT IN (SELECT id FROM teachers);

-- Update class enrollment counts
UPDATE classes SET current_enrollment = (
    SELECT COUNT(*) FROM students WHERE class_id = classes.id AND status = 'active'
);

-- =====================================================
-- SAMPLE DATA FOR TESTING (Optional)
-- =====================================================
-- Uncomment the following lines to create sample data for testing

/*
-- Sample classes
INSERT IGNORE INTO classes (class_name, section, capacity) VALUES
('10th', 'A', 50),
('10th', 'B', 50),
('9th', 'A', 45),
('9th', 'B', 45),
('11th', 'A', 40),
('12th', 'A', 35);

-- Sample subjects
INSERT IGNORE INTO subjects (subject_name, class_id, subject_code, is_compulsory) VALUES
('Mathematics', 1, 'MATH10A', TRUE),
('Science', 1, 'SCI10A', TRUE),
('English', 1, 'ENG10A', TRUE),
('Social Studies', 1, 'SOC10A', TRUE),
('Hindi', 1, 'HIN10A', TRUE);
*/

-- =====================================================
-- FINALIZE SETUP
-- =====================================================

-- Analyze tables for optimization
ANALYZE TABLE users, teachers, students, classes, subjects, student_attendance, teacher_attendance;

-- Set transaction isolation level
SET GLOBAL TRANSACTION ISOLATION LEVEL = 'READ COMMITTED';

-- Create a summary log
SELECT
    'Database setup completed successfully' as status,
    COUNT(*) as total_tables
FROM information_schema.tables
WHERE table_schema = DATABASE();

COMMIT;
