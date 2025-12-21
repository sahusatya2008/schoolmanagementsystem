# School Management System

A comprehensive school management system built with Python and MySQL designed by Satya Narayan Sahu of class 12th, and legally owns this software contents and the entire program. It is stricly prohibited to take anything from this content, if neended feel free to seek help from the author, on credits definately help will be given as per demanded. 

## Prerequisites

1. **MySQL Server** installed and running
2. **Python 3.x** installed
3. **pymysql** library: `pip install pymysql`

## Database Setup

### Option 1: Automatic Setup (Recommended)
Run the Python application. It will automatically:
- Connect to MySQL
- Create the database if it doesn't exist
- Create all required tables
- Set up default admin user

### Option 2: Manual Database Setup
If you prefer to set up the database manually:

1. **Create MySQL User** (run in MySQL shell as root):
   ```sql
   CREATE USER 'school_admin'@'localhost' IDENTIFIED BY 'your_secure_password';
   GRANT ALL PRIVILEGES ON school_management.* TO 'school_admin'@'localhost';
   GRANT CREATE, DROP ON *.* TO 'school_admin'@'localhost';
   FLUSH PRIVILEGES;
   ```

2. **Run the SQL Setup Script**:
   ```bash
   mysql -u root -p < setup_database.sql
   ```

   Or import through MySQL Workbench/phpMyAdmin.

## Configuration

The system uses these default database settings:
- **Host**: localhost
- **User**: root
- **Password**: root123
- **Database**: school_management

To use different settings, modify the connection parameters in `studentmanage.py` or set environment variables.

## Running the Application

```bash
python studentmanage.py
```

### Default Login Credentials
- **Username**: admin
- **Password**: admin123

## Database Schema

The system includes the following tables:
- `users` - System users and authentication
- `teachers` - Teacher profiles
- `students` - Student profiles
- `classes` - Class and section information
- `subjects` - Subject definitions
- `timetable` - Class schedules
- `student_attendance` - Student attendance records
- `teacher_attendance` - Teacher attendance records
- `teacher_privileges` - Teacher permission settings
- `student_status` - Student status management
- `teacher_status` - Teacher status management
- `teacher_assignments` - Teacher-class-subject assignments
- `teaching_records` - Teacher employment history
- `student_subjects` - Student-subject enrollments

## Complete MySQL Queries Reference

For a comprehensive reference of all SQL queries used in the system, see `complete_mysql_queries.sql`. This file contains:

- All table creation statements
- Database migration queries
- User authentication queries
- CRUD operations for all entities
- Complex JOIN queries for reporting
- Attendance management queries
- Privilege and status management
- Database maintenance operations

This file serves as complete documentation of the database layer.

## Features

- Multi-role user system (Admin, Teacher, Student, Principal, etc.)
- Student and teacher management
- Class and subject management
- Timetable creation
- Attendance tracking
- User privilege management
- Status management (active/suspended/removed)

## Troubleshooting

### Common Issues on New Devices

1. **MySQL Connection Failed**
   - Ensure MySQL server is installed and running
   - Check if the default credentials match your MySQL setup
   - Verify user has necessary privileges

2. **pymysql Import Error**
   ```bash
   pip install pymysql
   ```

3. **Database Creation Failed**
   - Ensure MySQL user has CREATE DATABASE privileges
   - Check MySQL service status

4. **Table Creation Errors**
   - Run the `setup_database.sql` script manually first
   - Check MySQL version compatibility

### Manual Database Verification

After setup, verify tables exist:
```sql
USE school_management;
SHOW TABLES;
```

Check default admin user:
```sql
SELECT * FROM users WHERE username = 'admin';
```

## Complete Database Setup SQL

If you need to manually set up the database, copy and paste the following SQL code into your MySQL client:

```sql
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

COMMIT;
```

## Security Notes

- Default passwords should be changed in production
- This software programs are owned by Satya Narayan Sahu, anything taken from this should be credited to the author.
- Consider using environment variables for database credentials
- The system uses SHA256 password hashing
- All database queries use parameterized statements to prevent SQL injection
