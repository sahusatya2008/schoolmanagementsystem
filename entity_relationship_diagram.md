# Entity Relationship Diagram (ERD)
## School Management System

**Version:** 1.0.0
**Date:** December 2024
**Author:** Satya Narayan Sahu

---

## Complete Entity Relationship Diagram

This document provides a comprehensive Entity Relationship Diagram (ERD) for the School Management System, showing all entities, attributes, and relationships with proper cardinality.

## ERD Notation

### Cardinality Symbols:
- **1:1** → One-to-One relationship
- **1:M** → One-to-Many relationship
- **M:M** → Many-to-Many relationship (resolved with junction tables)

### Relationship Types:
- **Identifying Relationship**: Strong relationship (child cannot exist without parent)
- **Non-Identifying Relationship**: Weak relationship (child can exist independently)

---

## Entity Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                                             │
│                                     SCHOOL MANAGEMENT SYSTEM ERD                                             │
│                                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│     USERS       │         │    TEACHERS     │         │    STUDENTS     │
│─────────────────│         │─────────────────│         │─────────────────│
│ PK id           │◄──1:1──►│ PK id           │         │ PK id           │
│ username (UQ)   │         │ FK user_id (UQ) │         │ FK user_id (UQ) │
│ password        │         │ name            │         │ admission_no(UQ)│
│ role (ENUM)     │         │ age             │         │ name            │
│ created_at      │         │ dob             │         │ age             │
│                 │         │ qualifications  │         │ dob             │
│                 │         │ teaching_subject│         │ FK class_id     │
└─────────────────┘         └─────────────────┘         │ previous_school │
          │                           │                 │ father_name     │
          │                           │                 │ mother_name     │
          │                           │                 │ father_occupation│
          │                           │                 │ mother_occupation│
          │                           │                 │ contact_number  │
          │                           │                 │ emergency_contact│
          └─────────────────┘         └─────────────────┘

           │                           │                 │
           │                           │                 │
           ▼                           ▼                 ▼

┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│TEACHER_PRIVILEGES│        │ TEACHER_STATUS  │         │ STUDENT_STATUS  │
│─────────────────│         │─────────────────│         │─────────────────│
│ PK id           │         │ PK id           │         │ PK id           │
│ FK teacher_id   │◄──1:1──►│ FK teacher_id   │◄──1:1──►│ FK student_id   │
│ can_edit_students│        │ status (ENUM)   │         │ status (ENUM)   │
│ can_delete_students│      │ suspension_reason│        │ suspension_reason│
│ can_suspend_students│     │ FK suspended_by │         │ FK suspended_by │
│ can_edit_subjects│        │ suspended_at    │         │ suspended_at    │
│ can_delete_subjects│      └─────────────────┘         └─────────────────┘
│ can_edit_attendance│
└─────────────────┘

           │                           │                 │
           │                           │                 │
           ▼                           ▼                 ▼

┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│TEACHING_RECORDS │         │TEACHER_ATTENDANCE│        │STUDENT_ATTENDANCE│
│─────────────────│         │─────────────────│         │─────────────────│
│ PK id           │         │ PK id           │         │ PK id           │
│ FK teacher_id   │◄──1:M──►│ FK teacher_id   │◄──1:M──►│ FK student_id   │
│ school_name     │         │ date (UQ)       │         │ date (UQ)       │
│ duration        │         │ status (ENUM)   │         │ status (ENUM)   │
│ position        │         │ FK recorded_by  │         │ FK recorded_by  │
│                 │         │ recorded_at     │         │ recorded_at     │
└─────────────────┘         └─────────────────┘         └─────────────────┘

┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│     CLASSES     │         │    SUBJECTS     │         │TEACHER_ASSIGNMENTS│
│─────────────────│         │─────────────────│         │──────────────────│
│ PK id           │         │ PK id           │         │ PK id             │
│ class_name      │◄──1:M──►│ FK class_id     │◄──1:M──►│ FK teacher_id     │
│ section (UQ)    │         │ subject_name    │         │ FK class_id       │
│                 │         │ FK teacher_id   │         │ FK subject_id     │
└─────────────────┘         └─────────────────┘         │ FK assigned_by    │
          ▲                           ▲                 │ assigned_at       │
          │                           │                 │ (UQ composite)    │
          │                           │                 └──────────────────┘
          │                           │
          │                           │
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│  STUDENT_SUBJECTS│        │   TIMETABLE     │         │  PROXY_TEACHERS  │
│──────────────────│        │─────────────────│         │──────────────────│
│ PK id            │        │ PK id           │         │ PK id             │
│ FK student_id    │◄──M:M──►│ FK class_id     │◄──1:M──►│ FK timetable_id  │
│ FK subject_id    │        │ day_of_week     │         │ FK original_teacher│
│                  │        │ lecture_number  │         │ FK proxy_teacher_id│
│                  │        │ start_time      │         │ proxy_date        │
│                  │        │ end_time        │         │ reason            │
│                  │        │ FK subject_id   │         │ FK assigned_by    │
│                  │        │ FK teacher_id   │         │ assigned_at       │
│                  │        │ break_start_time│         │ (UQ timetable_date)│
│                  │        │ break_end_time  │         └──────────────────┘
│                  │        │ FK created_by   │
│                  │        │ created_at      │
└──────────────────┘        └─────────────────┘
```

---

## Detailed Entity Descriptions

### 1. USERS Entity
**Primary Key:** id (AUTO_INCREMENT)
**Description:** Central authentication and role management table

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `username`: VARCHAR(100), Unique, Not Null
- `password`: VARCHAR(255), Not Null (SHA256 hashed)
- `role`: ENUM('admin', 'principal', 'teacher', 'student', 'system_admin', 'academic_coordinator', 'admission_department'), Not Null
- `created_at`: TIMESTAMP, Default CURRENT_TIMESTAMP

**Relationships:**
- **1:1** with TEACHERS (user_id)
- **1:1** with STUDENTS (user_id)
- **1:M** with STUDENT_ATTENDANCE (recorded_by)
- **1:M** with TEACHER_ATTENDANCE (recorded_by)
- **1:M** with TIMETABLE (created_by)
- **1:M** with TEACHER_ASSIGNMENTS (assigned_by)
- **1:M** with PROXY_TEACHERS (assigned_by)

### 2. TEACHERS Entity
**Primary Key:** id (AUTO_INCREMENT)
**Foreign Key:** user_id → USERS(id)
**Description:** Teacher profile and qualification information

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `user_id`: INT, Foreign Key, Unique
- `name`: VARCHAR(100), Not Null
- `age`: INT
- `dob`: DATE
- `highest_qualifications`: TEXT
- `teaching_subject`: VARCHAR(100)

**Relationships:**
- **1:1** with USERS (user_id)
- **1:1** with TEACHER_PRIVILEGES (teacher_id)
- **1:1** with TEACHER_STATUS (teacher_id)
- **1:M** with TEACHING_RECORDS (teacher_id)
- **1:M** with TEACHER_ATTENDANCE (teacher_id)
- **1:M** with SUBJECTS (teacher_id)
- **M:M** with CLASSES via TEACHER_ASSIGNMENTS
- **1:M** with TIMETABLE (teacher_id)
- **1:M** with PROXY_TEACHERS (original_teacher_id, proxy_teacher_id)

### 3. STUDENTS Entity
**Primary Key:** id (AUTO_INCREMENT)
**Foreign Key:** user_id → USERS(id), class_id → CLASSES(id)
**Description:** Student profile and academic information

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `user_id`: INT, Foreign Key, Unique
- `admission_number`: VARCHAR(50), Unique, Not Null
- `name`: VARCHAR(100), Not Null
- `age`: INT
- `dob`: DATE
- `class_id`: INT, Foreign Key
- `previous_school`: TEXT
- `father_name`: VARCHAR(100)
- `mother_name`: VARCHAR(100)
- `father_occupation`: VARCHAR(100)
- `mother_occupation`: VARCHAR(100)
- `contact_number`: VARCHAR(15)
- `emergency_contact`: VARCHAR(15)

**Relationships:**
- **1:1** with USERS (user_id)
- **1:1** with STUDENT_STATUS (student_id)
- **M:1** with CLASSES (class_id)
- **M:M** with SUBJECTS via STUDENT_SUBJECTS
- **1:M** with STUDENT_ATTENDANCE (student_id)

### 4. CLASSES Entity
**Primary Key:** id (AUTO_INCREMENT)
**Unique Key:** (class_name, section)
**Description:** Class and section definitions

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `class_name`: VARCHAR(50), Not Null
- `section`: VARCHAR(10), Not Null

**Relationships:**
- **1:M** with STUDENTS (class_id)
- **1:M** with SUBJECTS (class_id)
- **1:M** with TIMETABLE (class_id)
- **M:M** with TEACHERS via TEACHER_ASSIGNMENTS

### 5. SUBJECTS Entity
**Primary Key:** id (AUTO_INCREMENT)
**Foreign Keys:** class_id → CLASSES(id), teacher_id → TEACHERS(id)
**Description:** Subject definitions and teacher assignments

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `subject_name`: VARCHAR(100), Not Null
- `class_id`: INT, Foreign Key
- `teacher_id`: INT, Foreign Key

**Relationships:**
- **M:1** with CLASSES (class_id)
- **M:1** with TEACHERS (teacher_id)
- **M:M** with STUDENTS via STUDENT_SUBJECTS
- **1:M** with TIMETABLE (subject_id)
- **M:M** with TEACHERS via TEACHER_ASSIGNMENTS

### 6. STUDENT_SUBJECTS Entity (Junction Table)
**Primary Key:** id (AUTO_INCREMENT)
**Foreign Keys:** student_id → STUDENTS(id), subject_id → SUBJECTS(id)
**Description:** Resolves M:M relationship between students and subjects

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `student_id`: INT, Foreign Key
- `subject_id`: INT, Foreign Key

**Relationships:**
- **M:1** with STUDENTS (student_id)
- **M:1** with SUBJECTS (subject_id)

### 7. TIMETABLE Entity
**Primary Key:** id (AUTO_INCREMENT)
**Foreign Keys:** class_id → CLASSES(id), subject_id → SUBJECTS(id), teacher_id → TEACHERS(id), created_by → USERS(id)
**Description:** Class schedule and lecture timings

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `class_id`: INT, Foreign Key
- `day_of_week`: VARCHAR(15)
- `lecture_number`: INT
- `start_time`: TIME
- `end_time`: TIME
- `subject_id`: INT, Foreign Key
- `teacher_id`: INT, Foreign Key
- `break_start_time`: TIME
- `break_end_time`: TIME
- `created_by`: INT, Foreign Key
- `created_at`: TIMESTAMP, Default CURRENT_TIMESTAMP

**Relationships:**
- **M:1** with CLASSES (class_id)
- **M:1** with SUBJECTS (subject_id)
- **M:1** with TEACHERS (teacher_id)
- **M:1** with USERS (created_by)
- **1:M** with PROXY_TEACHERS (timetable_id)

### 8. STUDENT_ATTENDANCE Entity
**Primary Key:** id (AUTO_INCREMENT)
**Unique Key:** (student_id, date)
**Foreign Keys:** student_id → STUDENTS(id), recorded_by → USERS(id)
**Description:** Daily student attendance records

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `student_id`: INT, Foreign Key
- `date`: DATE, Not Null
- `status`: ENUM('present', 'absent'), Not Null
- `recorded_by`: INT, Foreign Key
- `recorded_at`: TIMESTAMP, Default CURRENT_TIMESTAMP

**Relationships:**
- **M:1** with STUDENTS (student_id)
- **M:1** with USERS (recorded_by)

### 9. TEACHER_ATTENDANCE Entity
**Primary Key:** id (AUTO_INCREMENT)
**Unique Key:** (teacher_id, date)
**Foreign Keys:** teacher_id → TEACHERS(id), recorded_by → USERS(id)
**Description:** Teacher attendance records

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `teacher_id`: INT, Foreign Key
- `date`: DATE, Not Null
- `status`: ENUM('present', 'absent'), Not Null
- `recorded_by`: INT, Foreign Key
- `recorded_at`: TIMESTAMP, Default CURRENT_TIMESTAMP

**Relationships:**
- **M:1** with TEACHERS (teacher_id)
- **M:1** with USERS (recorded_by)

### 10. TEACHER_PRIVILEGES Entity
**Primary Key:** id (AUTO_INCREMENT)
**Foreign Key:** teacher_id → TEACHERS(id)
**Description:** Granular permission settings for teachers

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `teacher_id`: INT, Foreign Key
- `can_edit_students`: BOOLEAN, Default FALSE
- `can_delete_students`: BOOLEAN, Default FALSE
- `can_suspend_students`: BOOLEAN, Default FALSE
- `can_edit_subjects`: BOOLEAN, Default FALSE
- `can_delete_subjects`: BOOLEAN, Default FALSE
- `can_edit_attendance`: BOOLEAN, Default FALSE

**Relationships:**
- **1:1** with TEACHERS (teacher_id)

### 11. STUDENT_STATUS Entity
**Primary Key:** id (AUTO_INCREMENT)
**Foreign Keys:** student_id → STUDENTS(id), suspended_by → USERS(id)
**Description:** Student status management (active/suspended/removed)

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `student_id`: INT, Foreign Key
- `status`: ENUM('active', 'suspended', 'removed'), Default 'active'
- `suspension_reason`: TEXT
- `suspended_by`: INT, Foreign Key
- `suspended_at`: TIMESTAMP, Default CURRENT_TIMESTAMP

**Relationships:**
- **1:1** with STUDENTS (student_id)
- **M:1** with USERS (suspended_by)

### 12. TEACHER_STATUS Entity
**Primary Key:** id (AUTO_INCREMENT)
**Foreign Keys:** teacher_id → TEACHERS(id), suspended_by → USERS(id)
**Description:** Teacher status management

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `teacher_id`: INT, Foreign Key
- `status`: ENUM('active', 'suspended', 'removed'), Default 'active'
- `suspension_reason`: TEXT
- `suspended_by`: INT, Foreign Key
- `suspended_at`: TIMESTAMP, Default CURRENT_TIMESTAMP

**Relationships:**
- **1:1** with TEACHERS (teacher_id)
- **M:1** with USERS (suspended_by)

### 13. TEACHER_ASSIGNMENTS Entity (Junction Table)
**Primary Key:** id (AUTO_INCREMENT)
**Unique Key:** (teacher_id, class_id, subject_id)
**Foreign Keys:** teacher_id → TEACHERS(id), class_id → CLASSES(id), subject_id → SUBJECTS(id), assigned_by → USERS(id)
**Description:** Resolves M:M relationship between teachers and class-subject combinations

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `teacher_id`: INT, Foreign Key
- `class_id`: INT, Foreign Key
- `subject_id`: INT, Foreign Key
- `assigned_by`: INT, Foreign Key
- `assigned_at`: TIMESTAMP, Default CURRENT_TIMESTAMP

**Relationships:**
- **M:1** with TEACHERS (teacher_id)
- **M:1** with CLASSES (class_id)
- **M:1** with SUBJECTS (subject_id)
- **M:1** with USERS (assigned_by)

### 14. PROXY_TEACHERS Entity
**Primary Key:** id (AUTO_INCREMENT)
**Unique Key:** (timetable_id, proxy_date)
**Foreign Keys:** timetable_id → TIMETABLE(id), original_teacher_id → TEACHERS(id), proxy_teacher_id → TEACHERS(id), assigned_by → USERS(id)
**Description:** Substitute teacher assignments for specific lectures

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `timetable_id`: INT, Foreign Key
- `original_teacher_id`: INT, Foreign Key
- `proxy_teacher_id`: INT, Foreign Key
- `proxy_date`: DATE
- `reason`: TEXT
- `assigned_by`: INT, Foreign Key
- `assigned_at`: TIMESTAMP, Default CURRENT_TIMESTAMP

**Relationships:**
- **M:1** with TIMETABLE (timetable_id)
- **M:1** with TEACHERS (original_teacher_id)
- **M:1** with TEACHERS (proxy_teacher_id)
- **M:1** with USERS (assigned_by)

### 15. TEACHING_RECORDS Entity
**Primary Key:** id (AUTO_INCREMENT)
**Foreign Key:** teacher_id → TEACHERS(id)
**Description:** Teacher employment history and experience

**Attributes:**
- `id`: INT, Primary Key, Auto Increment
- `teacher_id`: INT, Foreign Key
- `school_name`: VARCHAR(255)
- `duration`: VARCHAR(100)
- `position`: VARCHAR(100)

**Relationships:**
- **M:1** with TEACHERS (teacher_id)

---

## Relationship Summary

### One-to-One Relationships (1:1)
1. **USERS → TEACHERS** (user_id)
2. **USERS → STUDENTS** (user_id)
3. **TEACHERS → TEACHER_PRIVILEGES** (teacher_id)
4. **TEACHERS → TEACHER_STATUS** (teacher_id)
5. **STUDENTS → STUDENT_STATUS** (student_id)

### One-to-Many Relationships (1:M)
1. **USERS → STUDENT_ATTENDANCE** (recorded_by)
2. **USERS → TEACHER_ATTENDANCE** (recorded_by)
3. **USERS → TIMETABLE** (created_by)
4. **USERS → TEACHER_ASSIGNMENTS** (assigned_by)
5. **USERS → PROXY_TEACHERS** (assigned_by)
6. **USERS → STUDENT_STATUS** (suspended_by)
7. **USERS → TEACHER_STATUS** (suspended_by)
8. **TEACHERS → TEACHING_RECORDS** (teacher_id)
9. **TEACHERS → TEACHER_ATTENDANCE** (teacher_id)
10. **TEACHERS → SUBJECTS** (teacher_id)
11. **TEACHERS → TIMETABLE** (teacher_id)
12. **CLASSES → STUDENTS** (class_id)
13. **CLASSES → SUBJECTS** (class_id)
14. **CLASSES → TIMETABLE** (class_id)
15. **STUDENTS → STUDENT_ATTENDANCE** (student_id)
16. **SUBJECTS → TIMETABLE** (subject_id)
17. **TIMETABLE → PROXY_TEACHERS** (timetable_id)

### Many-to-Many Relationships (M:M) - Resolved with Junction Tables
1. **TEACHERS ↔ CLASSES** via **TEACHER_ASSIGNMENTS**
2. **TEACHERS ↔ SUBJECTS** via **TEACHER_ASSIGNMENTS**
3. **STUDENTS ↔ SUBJECTS** via **STUDENT_SUBJECTS**
4. **TEACHERS ↔ TIMETABLE** via **PROXY_TEACHERS** (for proxy assignments)

---

## Data Integrity Constraints

### Primary Key Constraints
- All entities have auto-incrementing integer primary keys
- Ensures unique identification of each record

### Foreign Key Constraints
- All foreign keys maintain referential integrity
- CASCADE deletion for dependent relationships
- SET NULL for optional relationships

### Unique Constraints
- **USERS**: username
- **STUDENTS**: admission_number, user_id
- **TEACHERS**: user_id
- **CLASSES**: (class_name, section)
- **STUDENT_ATTENDANCE**: (student_id, date)
- **TEACHER_ATTENDANCE**: (teacher_id, date)
- **TEACHER_ASSIGNMENTS**: (teacher_id, class_id, subject_id)
- **PROXY_TEACHERS**: (timetable_id, proxy_date)

### Check Constraints
- ENUM types restrict values to predefined sets
- Date validations ensure logical date ranges
- Length validations prevent buffer overflows

---

## Indexing Strategy

### Primary Indexes (Automatic)
- All primary keys are automatically indexed

### Foreign Key Indexes (Automatic)
- All foreign key columns are indexed for performance

### Additional Secondary Indexes
- **USERS**: username, role
- **TEACHERS**: user_id, name, teaching_subject
- **STUDENTS**: user_id, admission_number, name, class_id
- **SUBJECTS**: class_id, teacher_id, subject_name
- **TIMETABLE**: class_id, subject_id, teacher_id, day_of_week
- **STUDENT_ATTENDANCE**: student_id, date, recorded_by
- **TEACHER_ATTENDANCE**: teacher_id, date, recorded_by

### Composite Indexes
- **CLASSES**: (class_name, section)
- **STUDENT_ATTENDANCE**: (student_id, date)
- **TEACHER_ATTENDANCE**: (teacher_id, date)
- **TEACHER_ASSIGNMENTS**: (teacher_id, class_id, subject_id)
- **PROXY_TEACHERS**: (timetable_id, proxy_date)

---

## ERD Generation Information

**Diagram Tool:** ASCII Art with Mermaid-inspired notation
**Entities:** 15 core entities
**Relationships:** 25+ relationships documented
**Cardinality:** Properly defined for all relationships
**Attributes:** Key attributes shown for each entity
**Constraints:** Primary keys, foreign keys, and unique constraints indicated

**Document Version:** 1.0.0
**Last Updated:** December 2024
**Author:** Satya Narayan Sahu