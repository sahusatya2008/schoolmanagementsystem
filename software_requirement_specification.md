# Software Requirements Specification (SRS)
## School Management System

**Version:** 1.0.0  
**Date:** December 2024  
**Author:** Satya Narayan Sahu  

---

## Table of Contents

1. [Introduction](#1-introduction)
   1.1 [Purpose](#11-purpose)
   1.2 [Scope](#12-scope)
   1.3 [Definitions, Acronyms, and Abbreviations](#13-definitions-acronyms-and-abbreviations)
   1.4 [References](#14-references)
   1.5 [Overview](#15-overview)

2. [Overall Description](#2-overall-description)
   2.1 [Product Perspective](#21-product-perspective)
   2.2 [Product Functions](#22-product-functions)
   2.3 [User Characteristics](#23-user-characteristics)
   2.4 [Constraints](#24-constraints)
   2.5 [Assumptions and Dependencies](#25-assumptions-and-dependencies)

3. [Specific Requirements](#3-specific-requirements)
   3.1 [External Interface Requirements](#31-external-interface-requirements)
   3.2 [Functional Requirements](#32-functional-requirements)
   3.3 [Performance Requirements](#33-performance-requirements)
   3.4 [Design Constraints](#34-design-constraints)
   3.5 [Software System Attributes](#35-software-system-attributes)
   3.6 [Database Requirements](#36-database-requirements)
   3.7 [Security Requirements](#37-security-requirements)

---

## 1. Introduction

### 1.1 Purpose

The School Management System (SMS) is a comprehensive software solution designed to automate and streamline the administrative, academic, and operational activities of educational institutions following the CBSE curriculum. The system aims to digitize traditional school management processes, improve efficiency, reduce paperwork, and provide real-time access to critical information for all stakeholders.

### 1.2 Scope

The system will provide:

- **Multi-role User Management**: Support for administrators, teachers, students, principals, academic coordinators, and admission department staff
- **Student Information Management**: Complete lifecycle management from admission to graduation
- **Teacher Management**: Profile management, privilege assignment, and performance tracking
- **Academic Management**: Class, subject, and timetable management
- **Attendance Tracking**: Real-time attendance monitoring for students and teachers
- **Reporting System**: Comprehensive reports for academic and administrative purposes
- **Database Management**: Robust MySQL database with data integrity and backup capabilities

**Out of Scope:**
- Online examination system
- Fee management and billing
- Library management
- Transportation management
- Hostel management
- Mobile application development

### 1.3 Definitions, Acronyms, and Abbreviations

| Term | Definition |
|------|------------|
| SMS | School Management System |
| CBSE | Central Board of Secondary Education |
| MySQL | Relational Database Management System |
| SHA256 | Secure Hash Algorithm 256-bit |
| GUI | Graphical User Interface |
| CRUD | Create, Read, Update, Delete |
| FK | Foreign Key |
| PK | Primary Key |
| SRS | Software Requirements Specification |

### 1.4 References

- IEEE Standard for Software Requirements Specifications (IEEE 830-1998)
- CBSE Curriculum Guidelines
- MySQL 8.0 Documentation
- Python 3.8+ Documentation
- PyMySQL Library Documentation

### 1.5 Overview

This SRS document provides a comprehensive description of the functional and non-functional requirements for the School Management System. The document is organized into three main sections: Introduction, Overall Description, and Specific Requirements.

---

## 2. Overall Description

### 2.1 Product Perspective

The School Management System is a standalone desktop application that operates on Windows, macOS, and Linux platforms. It interfaces with a MySQL database server for data persistence and uses a command-line interface for user interaction.

**System Context Diagram:**

```
[School Management System]
    |
    |---[MySQL Database Server]
    |       |
    |       |---[User Authentication Data]
    |       |---[Student Records]
    |       |---[Teacher Records]
    |       |---[Academic Data]
    |       |---[Attendance Data]
    |
    |---[System Users]
            |
            |---[Administrators]
            |---[Teachers]
            |---[Students]
            |---[Principals]
            |---[Academic Coordinators]
            |---[Admission Department]
```

### 2.2 Product Functions

The major functions of the system include:

1. **User Management**: Create, modify, and manage user accounts with role-based access
2. **Student Management**: Handle student admissions, profiles, class assignments, and status tracking
3. **Teacher Management**: Manage teacher profiles, privileges, assignments, and performance
4. **Academic Management**: Create and manage classes, subjects, and timetables
5. **Attendance Management**: Record and track attendance for students and teachers
6. **Reporting**: Generate various reports for academic and administrative purposes
7. **Database Maintenance**: Backup, restore, and optimize database operations

### 2.3 User Characteristics

#### Administrator
- Technical expertise: High
- Computer literacy: Expert
- Frequency of use: Daily
- Training required: Minimal (system familiarization)

#### Teacher
- Technical expertise: Medium
- Computer literacy: Intermediate
- Frequency of use: Daily
- Training required: Basic computer skills

#### Student
- Technical expertise: Low
- Computer literacy: Basic
- Frequency of use: Weekly
- Training required: Minimal guidance

#### Principal/Academic Coordinator
- Technical expertise: Medium-High
- Computer literacy: Intermediate-Advanced
- Frequency of use: Daily
- Training required: Basic system overview

### 2.4 Constraints

#### Technical Constraints
- **Platform**: Windows 10+, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Database**: MySQL 8.0 or higher
- **Programming Language**: Python 3.8+
- **Memory**: Minimum 2GB RAM, Recommended 4GB+
- **Storage**: Minimum 500MB free space
- **Network**: Local network access to MySQL server

#### Regulatory Constraints
- **Data Privacy**: Compliance with local data protection regulations
- **Educational Standards**: Adherence to CBSE curriculum guidelines
- **Security**: Implementation of industry-standard security practices

#### Business Constraints
- **Budget**: Cost-effective solution for educational institutions
- **Timeline**: Development and deployment within specified timeframe
- **Scalability**: Support for schools with 500-5000 students

### 2.5 Assumptions and Dependencies

#### Assumptions
- MySQL server is properly installed and configured
- Users have basic computer literacy
- Network connectivity is stable for database operations
- School follows CBSE curriculum structure
- System will be used in a controlled environment

#### Dependencies
- MySQL Server 8.0+
- Python 3.8+ runtime environment
- PyMySQL library for database connectivity
- Operating system compatibility
- Hardware meeting minimum requirements

---

## 3. Specific Requirements

### 3.1 External Interface Requirements

#### User Interfaces
- **Command-line Interface**: Text-based menu-driven interface
- **Input Methods**: Keyboard input for all data entry
- **Output Methods**: Console display for information and reports
- **Error Handling**: Clear error messages with resolution guidance

#### Hardware Interfaces
- **Database Server**: MySQL server running on localhost or network
- **Storage**: Local file system for logs and temporary files
- **Backup Media**: External storage for database backups

#### Software Interfaces
- **Operating System**: Windows, macOS, or Linux
- **Database Management System**: MySQL 8.0+
- **Python Libraries**: PyMySQL for database connectivity

#### Communication Interfaces
- **Database Connection**: TCP/IP connection to MySQL server
- **Local Network**: For multi-user access in network deployments

### 3.2 Functional Requirements

#### 3.2.1 User Authentication and Authorization

**SRS-USER-001**: User Login
- **Description**: System shall authenticate users based on username and password
- **Priority**: High
- **Inputs**: Username, password
- **Outputs**: Authentication success/failure, user role assignment
- **Pre-conditions**: Valid user account exists
- **Post-conditions**: User session established with appropriate permissions

**SRS-USER-002**: Role-Based Access Control
- **Description**: System shall restrict access based on user roles
- **Priority**: High
- **Inputs**: User role from authentication
- **Outputs**: Menu options appropriate to user role
- **Pre-conditions**: Successful authentication
- **Post-conditions**: User interface displays role-appropriate options

#### 3.2.2 Student Management

**SRS-STUDENT-001**: Add New Student
- **Description**: System shall allow creation of new student records
- **Priority**: High
- **Inputs**: Student details (name, admission number, DOB, contact info, etc.)
- **Outputs**: Confirmation of student creation, unique student ID
- **Pre-conditions**: User has student creation privileges
- **Post-conditions**: Student record stored in database

**SRS-STUDENT-002**: Update Student Information
- **Description**: System shall allow modification of existing student records
- **Priority**: Medium
- **Inputs**: Student ID, updated information
- **Outputs**: Confirmation of update
- **Pre-conditions**: Student exists, user has update privileges
- **Post-conditions**: Database updated with new information

**SRS-STUDENT-003**: View Student Profile
- **Description**: System shall display complete student information
- **Priority**: Medium
- **Inputs**: Student ID or search criteria
- **Outputs**: Complete student profile
- **Pre-conditions**: Student exists in database
- **Post-conditions**: Information displayed to user

#### 3.2.3 Teacher Management

**SRS-TEACHER-001**: Add New Teacher
- **Description**: System shall create new teacher records with profile information
- **Priority**: High
- **Inputs**: Teacher details (name, qualifications, subjects, contact info)
- **Outputs**: Teacher ID and confirmation
- **Pre-conditions**: User has teacher creation privileges
- **Post-conditions**: Teacher record stored with default privileges

**SRS-TEACHER-002**: Assign Teacher Privileges
- **Description**: System shall configure teacher permissions for various operations
- **Priority**: High
- **Inputs**: Teacher ID, privilege settings
- **Outputs**: Updated privilege confirmation
- **Pre-conditions**: Teacher exists, user has privilege management rights
- **Post-conditions**: Teacher permissions updated in database

#### 3.2.4 Academic Management

**SRS-ACADEMIC-001**: Create Class
- **Description**: System shall create new class-section combinations
- **Priority**: High
- **Inputs**: Class name, section
- **Outputs**: Class ID and confirmation
- **Pre-conditions**: Class doesn't already exist
- **Post-conditions**: Class record stored in database

**SRS-ACADEMIC-002**: Add Subject
- **Description**: System shall create new subject records
- **Priority**: High
- **Inputs**: Subject name, class association
- **Outputs**: Subject ID and confirmation
- **Pre-conditions**: Valid class exists
- **Post-conditions**: Subject stored with class relationship

**SRS-ACADEMIC-003**: Create Timetable
- **Description**: System shall generate class timetables with subject assignments
- **Priority**: Medium
- **Inputs**: Class ID, subject assignments, time slots
- **Outputs**: Complete timetable structure
- **Pre-conditions**: Classes and subjects exist
- **Post-conditions**: Timetable stored in database

#### 3.2.5 Attendance Management

**SRS-ATTENDANCE-001**: Mark Student Attendance
- **Description**: System shall record daily student attendance
- **Priority**: High
- **Inputs**: Student ID, date, attendance status
- **Outputs**: Attendance record confirmation
- **Pre-conditions**: Student exists, user has attendance privileges
- **Post-conditions**: Attendance data stored with timestamp

**SRS-ATTENDANCE-002**: View Attendance Reports
- **Description**: System shall generate attendance reports for students
- **Priority**: Medium
- **Inputs**: Student ID, date range
- **Outputs**: Attendance summary and detailed records
- **Pre-conditions**: Attendance data exists
- **Post-conditions**: Report displayed to user

#### 3.2.6 Reporting

**SRS-REPORT-001**: Generate Student Reports
- **Description**: System shall create comprehensive student reports
- **Priority**: Medium
- **Inputs**: Report type, filters, date ranges
- **Outputs**: Formatted report data
- **Pre-conditions**: Sufficient data exists
- **Post-conditions**: Report displayed or exported

### 3.3 Performance Requirements

#### Response Time
- **User Authentication**: < 2 seconds
- **Database Queries**: < 5 seconds for complex reports
- **Data Entry Operations**: < 1 second
- **Report Generation**: < 30 seconds for standard reports

#### Throughput
- **Concurrent Users**: Support for 10-20 simultaneous users
- **Database Transactions**: 100 transactions per minute
- **Data Processing**: Handle 1000+ student records efficiently

#### Resource Utilization
- **Memory Usage**: < 500MB during normal operation
- **CPU Usage**: < 20% during peak usage
- **Storage**: Efficient use of database storage with proper indexing

### 3.4 Design Constraints

#### Software Constraints
- **Programming Language**: Python 3.8+ only
- **Database**: MySQL 8.0+ only
- **GUI Framework**: Command-line interface only
- **External Libraries**: Limited to PyMySQL for database connectivity

#### Hardware Constraints
- **Minimum RAM**: 2GB
- **Recommended RAM**: 4GB+
- **Storage**: 500MB free space
- **Network**: Stable LAN connection for database access

#### Standards Compliance
- **Database Design**: Follow relational database normalization principles
- **Security**: Implement industry-standard password hashing (SHA256)
- **Data Integrity**: Use foreign key constraints and referential integrity
- **Code Quality**: Follow PEP 8 Python coding standards

### 3.5 Software System Attributes

#### Security
- Password encryption using SHA256 hashing
- Role-based access control
- SQL injection prevention through parameterized queries
- Secure database connections

#### Reliability
- System availability: 99% uptime
- Data integrity: 100% (ACID compliance)
- Error recovery: Automatic rollback on transaction failures
- Backup and recovery procedures

#### Usability
- Intuitive menu-driven interface
- Clear error messages and help text
- Consistent navigation patterns
- Minimal training requirements

#### Portability
- Cross-platform compatibility (Windows, macOS, Linux)
- Database server independence (local or network)
- Easy deployment and configuration

#### Maintainability
- Modular code structure
- Comprehensive documentation
- Clear separation of concerns
- Easy database schema updates

### 3.6 Database Requirements

#### Database Management System
- **Type**: MySQL 8.0+
- **Architecture**: Relational database
- **Character Set**: UTF-8
- **Storage Engine**: InnoDB (for ACID compliance)

#### Database Schema

**Core Tables:**
1. `users` - User authentication and roles
2. `teachers` - Teacher profile information
3. `students` - Student profile information
4. `classes` - Class and section definitions
5. `subjects` - Subject definitions
6. `timetable` - Class schedules
7. `student_attendance` - Daily attendance records
8. `teacher_attendance` - Teacher attendance records
9. `teacher_privileges` - Permission settings
10. `student_status` - Student status management
11. `teacher_status` - Teacher status management
12. `teacher_assignments` - Teacher-class-subject relationships
13. `teaching_records` - Teacher employment history
14. `student_subjects` - Student-subject enrollments

#### Data Integrity
- Primary key constraints on all tables
- Foreign key relationships with CASCADE/SET NULL actions
- Unique constraints on critical fields
- NOT NULL constraints on required fields
- Data type validation at database level

#### Performance Requirements
- Proper indexing on frequently queried columns
- Optimized queries for reporting functions
- Connection pooling for multiple users
- Regular maintenance and optimization procedures

### 3.7 Security Requirements

#### Authentication
- Secure password storage with SHA256 hashing
- Account lockout after multiple failed attempts
- Session management with automatic timeout
- Secure password reset procedures

#### Authorization
- Role-based access control (RBAC)
- Granular permissions for different operations
- Privilege escalation prevention
- Audit logging of sensitive operations

#### Data Protection
- Encryption of sensitive data at rest
- Secure database connections
- Input validation and sanitization
- SQL injection prevention

#### Audit and Compliance
- Comprehensive audit logging
- Regular security updates
- Data backup and recovery procedures
- Compliance with data protection regulations

---

## Appendices

### Appendix A: Database Schema Details

#### Table: users
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

#### Table: teacher_privileges
```sql
CREATE TABLE teacher_privileges (
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
```

### Appendix B: User Role Permissions Matrix

| Function | Admin | Principal | Teacher | Student | Academic Coord | Admission Dept |
|----------|-------|-----------|---------|---------|----------------|----------------|
| User Management | Full | Read | None | None | Limited | Limited |
| Student Management | Full | Read | Limited | Personal | Limited | Full |
| Teacher Management | Full | Read | Personal | None | Limited | None |
| Attendance | Full | Read | Class | Personal | Read | None |
| Reports | Full | Full | Class | Personal | Academic | Enrollment |

### Appendix C: System Test Cases

#### Test Case 1: User Authentication
- **Input**: Valid username/password
- **Expected Output**: Successful login with appropriate menu
- **Pass Criteria**: User role correctly identified and menu displayed

#### Test Case 2: Student Creation
- **Input**: Complete student information
- **Expected Output**: Student record created with unique ID
- **Pass Criteria**: Student appears in database with correct information

#### Test Case 3: Attendance Marking
- **Input**: Student ID, date, attendance status
- **Expected Output**: Attendance record stored
- **Pass Criteria**: Record appears in attendance table with correct data

---

**Document Version Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0.0 | Dec 2024 | Satya Narayan Sahu | Initial release |

**Approval**

This Software Requirements Specification has been reviewed and approved for the development of the School Management System.

**Approved By:**  
Satya Narayan Sahu  
Project Manager  
Date: December 2024
