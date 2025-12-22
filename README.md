# School Management System v1 by SNS

A comprehensive school management system built with Python and MySQL designed by Satya Narayan Sahu of class 12th, and legally owns this software contents and the entire program. It is stricly prohibited to take anything from this content, if neended feel free to seek help from the author, on credits definately help will be given as per demanded. 

## Complete Documentation
---

## IMMEDIATE FIX: "Unknown column 'tp.can_edit_attendance'" Error

**If you see this error, here's the quick fix:**

```bash
# 1. Navigate to project directory
cd schoolmanagementsystem

# 2. Run diagnostic to check what's wrong
./diagnose_database.sh

# 3. Apply the fix
mysql -u root -p < update_database.sql

# 4. Verify it worked
python studentmanage.py
```

**For detailed troubleshooting, see the [Database Error Solutions](#database-error-solutions) section below.**

---

## Table of Contents

- [System Overview](#system-overview)
- [Prerequisites](#prerequisites)
- [Installation Guide](#installation-guide)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [User Roles & Features](#user-roles--features)
- [Database Schema](#database-schema)
- [Project Files](#project-files)
- [Database Error Solutions](#database-error-solutions)
- [Performance Optimization](#performance-optimization)
- [Troubleshooting](#troubleshooting)
- [Security](#security)
- [API Reference](#api-reference)

---

## System Overview

The School Management System is designed for CBSE curriculum schools and provides:

- **Multi-role User Management**: Admin, Principal, Teachers, Students, Academic Coordinators, Admission Department
- **Complete Student Lifecycle**: Admission, class assignment, attendance, performance tracking
- **Teacher Management**: Profiles, privileges, assignments, attendance
- **Academic Management**: Classes, subjects, timetables, curriculum planning
- **Administrative Functions**: Reports, status management, database maintenance

### Key Features:
- Role-based access control
- Real-time attendance tracking
- Automated subject assignments
- Comprehensive reporting
- Database integrity with foreign keys
- SHA256 password encryption
- SQL injection prevention

---

## Prerequisites

### Required Software:
1. **MySQL Server 8.0+** (Community Edition)
   - Linux: `sudo apt install mysql-server`
   - macOS: `brew install mysql`
   - Windows: Download from mysql.com

2. **Python 3.8+**
   - Linux/macOS: Usually pre-installed
   - Windows: Download from python.org

3. **Python Libraries**
   ```bash
   pip install pymysql
   ```

### System Requirements:
- **RAM**: Minimum 2GB, Recommended 4GB+
- **Storage**: 500MB free space
- **OS**: Linux, macOS, or Windows

### MySQL Configuration:
Ensure MySQL service is running:
```bash
# Linux
sudo systemctl status mysql

# macOS
brew services list | grep mysql

# Windows
services.msc (look for MySQL)
```

---

## Installation Guide

### Step 1: Download/Clone the Project
```bash
# If downloaded as ZIP, extract to a folder
unzip school-management-system.zip
cd schoolmanagementsystem
```

### Step 2: Install Python Dependencies
```bash
pip install pymysql
```

### Step 3: Verify MySQL Installation
```bash
mysql --version
mysql -u root -p -e "SELECT VERSION();"
```

### Step 4: Database Setup (Choose One Method)

#### Method A: Automatic Setup (Recommended)
```bash
python studentmanage.py
```
The system will automatically create the database and tables on first run.

#### Method B: Manual Setup
```bash
# Create database
mysql -u root -p -e "CREATE DATABASE school_management;"

# Run setup script
mysql -u root -p school_management < setup_database.sql
```

#### Method C: Fast Setup (For Large Databases)
```bash
chmod +x fast_mysql_setup.sh
./fast_mysql_setup.sh
```

---

## Database Setup

### Database Configuration
The system uses these default settings (configured in `studentmanage.py`):

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root123',
    'database': 'school_management'
}
```

### Database Schema Overview

The system creates 13 interconnected tables:

1. **`users`** - Authentication and user roles
2. **`teachers`** - Teacher profiles and information
3. **`students`** - Student profiles and information
4. **`classes`** - Class and section definitions
5. **`subjects`** - Subject definitions and assignments
6. **`timetable`** - Class schedules and lectures
7. **`student_attendance`** - Daily attendance records
8. **`teacher_attendance`** - Teacher attendance records
9. **`teacher_privileges`** - Permission settings for teachers
10. **`student_status`** - Student status management (active/suspended/removed)
11. **`teacher_status`** - Teacher status management
12. **`teacher_assignments`** - Teacher-class-subject relationships
13. **`teaching_records`** - Teacher employment history
14. **`student_subjects`** - Student-subject enrollments

### Default Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Administrator

**Important**: Change the default password after first login!

---

## Running the Application

### Basic Startup
```bash
cd schoolmanagementsystem
python studentmanage.py
```

### First-Time Setup
1. Run the application
2. The system will automatically create the database if it doesn't exist
3. Login with admin/admin123
4. Change the default password immediately

### User Interface
The system provides a menu-driven interface with role-based dashboards:

- **Admin Dashboard**: Complete system management
- **Teacher Dashboard**: Class and student management
- **Student Dashboard**: Personal information and attendance
- **Principal Dashboard**: Read-only system overview
- **Academic Coordinator**: Curriculum management
- **Admission Department**: Student enrollment

---

## User Roles & Features

### 1. Administrator (admin)
**Full System Access:**
- Create/manage all users (teachers, students, principals, etc.)
- Manage classes, subjects, and timetables
- Configure teacher privileges
- Database maintenance and cleanup
- System-wide reporting

### 2. Teacher
**Class Management:**
- Mark student attendance
- View assigned classes and subjects
- Access student profiles (limited by privileges)
- View personal timetable and attendance
- Manage student status (if privileged)

### 3. Student
**Personal Access:**
- View personal profile and attendance
- Check class timetable
- View assigned subjects and teachers
- Monitor attendance percentage

### 4. Principal
**Read-Only Oversight:**
- View all system data
- Access comprehensive reports
- Monitor teacher and student performance
- No modification capabilities

### 5. Academic Coordinator
**Curriculum Management:**
- Subject and timetable planning
- Academic performance analysis
- Curriculum development

### 6. Admission Department
**Enrollment Management:**
- Student admissions
- Class capacity monitoring
- Enrollment statistics

---

## Database Schema Details

### Core Tables Structure:

#### `users` Table
```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin', 'principal', 'teacher', 'student',
             'system_admin', 'academic_coordinator', 'admission_department') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### `teacher_privileges` Table
```sql
CREATE TABLE teacher_privileges (
    id INT AUTO_INCREMENT PRIMARY KEY,
    teacher_id INT,
    can_edit_students BOOLEAN DEFAULT FALSE,
    can_delete_students BOOLEAN DEFAULT FALSE,
    can_suspend_students BOOLEAN DEFAULT FALSE,
    can_edit_subjects BOOLEAN DEFAULT FALSE,
    can_delete_subjects BOOLEAN DEFAULT FALSE,
    can_edit_attendance BOOLEAN DEFAULT FALSE,  -- This column was missing!
    FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
);
```

### Relationships:
- **Users** → **Teachers** (1:1, user_id)
- **Users** → **Students** (1:1, user_id)
- **Classes** ←→ **Subjects** (1:many)
- **Teachers** ←→ **Subjects** (many:many via teacher_assignments)
- **Students** ←→ **Subjects** (many:many via student_subjects)
- **Classes** ←→ **Students** (1:many, class_id)

---

## Project Files

| File | Purpose | Size |
|------|---------|------|
| `studentmanage.py` | Main application | ~4.6MB |
| `setup_database.sql` | Complete database schema | ~3KB |
| `complete_mysql_queries.sql` | All SQL queries reference | ~15KB |
| `README.md` | This documentation | ~8KB |
| `.gitignore` | Version control | ~100B |

---

## Database Error Solutions

### **CRITICAL: "Unknown column 'tp.can_edit_attendance'" Error**

This is the most common error users encounter. Here's the complete solution guide:

#### **What Causes This Error:**
- The `teacher_privileges` table is missing the `can_edit_attendance` column
- Application code expects this column but database schema doesn't include it
- Usually happens with incomplete installations or old setup files

#### **Immediate Solutions (Choose One):**

##### **Solution 1: One-Command Fix (Fastest)**
```bash
cd schoolmanagementsystem
mysql -u root -p -e "USE school_management; ALTER TABLE teacher_privileges ADD COLUMN can_edit_attendance BOOLEAN DEFAULT FALSE;"
```

##### **Solution 2: Use Update Script (Recommended)**
```bash
cd schoolmanagementsystem
mysql -u root -p < update_database.sql
```

##### **Solution 3: Diagnostic + Fix**
```bash
cd schoolmanagementsystem
./diagnose_database.sh
# Follow the recommendations provided
```

##### **Solution 4: Complete Database Reset**
```bash
cd schoolmanagementsystem
./mysql_force_reset.sh
# Choose option 3: "Reset database (drop + recreate + setup)"
```

##### **Solution 5: Manual Step-by-Step**
```bash
# 1. Connect to MySQL
mysql -u root -p

# 2. Use the database
USE school_management;

# 3. Add the missing column
ALTER TABLE teacher_privileges ADD COLUMN can_edit_attendance BOOLEAN DEFAULT FALSE;

# 4. Verify it worked
DESCRIBE teacher_privileges;

# 5. Exit
EXIT;
```

#### **Verification Commands:**
```sql
-- Check if column exists
USE school_management;
DESCRIBE teacher_privileges;

-- Should show:
-- can_edit_attendance | tinyint(1) | YES |     | 0 |

-- Test the application
-- Run: python studentmanage.py
-- Login and try teacher privilege management
```

#### **Prevention:**
- Always use `setup_database.sql` for new installations
- Run `update_database.sql` when upgrading
- Use `./diagnose_database.sh` before reporting issues

#### **If Error Persists:**
1. Check MySQL user permissions
2. Verify database name is correct
3. Ensure no other MySQL processes are interfering
4. Try the force reset script

---

## Performance Optimization

### MySQL Performance Tips:

#### **1. Use Fast Setup Script**
```bash
./fast_mysql_setup.sh  # 10x faster than regular import
```

#### **2. Optimize MySQL Configuration**
Add to `/etc/mysql/mysql.conf.d/mysqld.cnf`:
```ini
[mysqld]
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
query_cache_size = 256M
max_connections = 200
```

#### **3. Database Maintenance**
```sql
-- Regular optimization
OPTIMIZE TABLE users, teachers, students, classes, subjects;
ANALYZE TABLE users, teachers, students, classes, subjects;
```

#### **4. Index Optimization**
The system includes proper indexes on foreign keys and frequently queried columns.

---

## Troubleshooting

### Common Issues & Solutions:

#### **1. MySQL Connection Failed**
```bash
# Check if MySQL is running
sudo systemctl status mysql

# Start MySQL
sudo systemctl start mysql

# Reset root password if needed
sudo mysql_secure_installation
```

#### **2. pymysql Import Error**
```bash
pip install pymysql
# Or
pip3 install pymysql
```

#### **3. Permission Denied**
```sql
-- Grant proper permissions
GRANT ALL PRIVILEGES ON school_management.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
```

#### **4. Frozen MySQL Process**
```bash
# Kill frozen processes
./mysql_force_reset.sh
# Choose option 1 or 2
```

#### **5. Database Corruption**
```bash
# Complete reset
./mysql_force_reset.sh
# Choose option 4: "Full system reset"
```

### Diagnostic Tools:

#### **Run Health Check:**
```bash
./diagnose_database.sh
```

#### **Check MySQL Logs:**
```bash
# Linux
sudo tail -f /var/log/mysql/error.log

# macOS
tail -f /usr/local/var/mysql/MacBook-Pro.local.err
```

#### **Monitor Processes:**
```bash
ps aux | grep mysql
```

---

## Security

### Password Security:
- SHA256 hashing for all passwords
- Salted password storage
- No plain text passwords in logs

### Database Security:
- Parameterized queries prevent SQL injection
- Foreign key constraints maintain data integrity
- Role-based access control

### Best Practices:
1. Change default admin password immediately
2. Use strong passwords for all users
3. Regularly backup the database
4. Keep MySQL server updated
5. Use environment variables for sensitive data

### Security Checklist:
- Foreign key constraints
- Role-based permissions
- Input validation
- Error handling without data leakage
- Default passwords should be changed in production
- This software programs are owned by Satya Narayan Sahu, anything taken from this should be credited to the author.
- Consider using environment variables for database credentials
- The system uses SHA256 password hashing
- All database queries use parameterized statements to prevent SQL injection



---

## API Reference

### Database Tables Reference:

#### **Users Table**
- `id`: Primary key
- `username`: Unique login name
- `password`: SHA256 hashed password
- `role`: User role enum
- `created_at`: Registration timestamp

#### **Teacher Privileges Table**
- `id`: Primary key
- `teacher_id`: Foreign key to teachers
- `can_edit_students`: Boolean permission
- `can_delete_students`: Boolean permission
- `can_suspend_students`: Boolean permission
- `can_edit_subjects`: Boolean permission
- `can_delete_subjects`: Boolean permission
- `can_edit_attendance`: Boolean permission

### Key SQL Queries:

#### **User Authentication:**
```sql
SELECT * FROM users WHERE username = %s AND password = %s;
```

#### **Teacher Privilege Check:**
```sql
SELECT can_edit_attendance FROM teacher_privileges WHERE teacher_id = (SELECT id FROM teachers WHERE user_id = %s);
```

#### **Student Attendance:**
```sql
INSERT INTO student_attendance (student_id, date, status, recorded_by) VALUES (%s, %s, %s, %s);
```

### Complete SQL Reference:
See `complete_mysql_queries.sql` for all database operations used in the system.

---

## Getting Started

1. **Install Prerequisites**
2. **Run Setup**: `./fast_mysql_setup.sh`
3. **Start Application**: `python studentmanage.py`
4. **Login**: admin / admin123
5. **Change Password**: Go to admin settings
6. **Create Users**: Add teachers, students, classes
7. **Configure System**: Set up subjects, timetables, privileges

## Support

If you encounter issues:

1. Run `./diagnose_database.sh` for automatic diagnosis
2. Check the troubleshooting section above
3. Verify all prerequisites are installed
4. Ensure MySQL is running and accessible

## License

This School Management System is provided as-is for educational and institutional use and it is owned by Satya Narayan Sahu

---

**Last Updated**: December 2024
**Version**: 1.0.0
**Compatibility**: MySQL 8.0+, Python 3.8+
**Signed**: Satya Narayan Sahu
