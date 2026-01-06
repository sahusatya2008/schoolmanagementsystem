import pymysql
from datetime import datetime, date
import getpass
import sys
import hashlib
import os
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DatabaseConfig:
    """
    Database Configuration Manager

    This class securely manages MySQL database connection parameters by prioritizing
    environment variables for sensitive data while falling back to user prompts.
    It implements connection validation to ensure database accessibility before
    proceeding with application startup.

    The class supports flexible configuration through environment variables:
    - DB_HOST: Database server hostname (default: localhost)
    - DB_USER: Database username (default: root)
    - DB_PASSWORD: Database password (prompted if not set)
    - DB_NAME: Target database name (default: school_management)
    - DB_PORT: Database server port (default: 3306)

    Attributes:
        host (str): MySQL server hostname or IP address.
        user (str): MySQL database username for authentication.
        password (str): MySQL user password (securely prompted if missing).
        database (str): Name of the target database to connect to.
        port (int): MySQL server port number.
        charset (str): Character set for database connection (UTF-8 default).

    Methods:
        __init__(): Initializes configuration with secure credential handling.
        _test_connection(): Validates database server connectivity.
        get_connection_params(): Returns complete connection parameters dictionary.

    Raises:
        SystemExit: If database connection test fails after configuration setup.
    """

    def __init__(self):
        """
        Initialize database configuration with secure credential handling.

        Reads database connection parameters from environment variables with sensible defaults.
        Prompts user for password if not provided via environment. Validates connection
        to ensure database server is accessible before proceeding.

        Raises:
            SystemExit: If database connection test fails.
        """
        self.host = os.getenv('DB_HOST', 'localhost')
        self.user = os.getenv('DB_USER', 'root')
        self.password = os.getenv('DB_PASSWORD', '')
        self.database = os.getenv('DB_NAME', 'school_management')
        self.port = int(os.getenv('DB_PORT', '3306'))
        self.charset = 'utf8mb4'

        # If password not set via environment, prompt user
        if not self.password:
            print("Database password not found in environment variables.")
            self.password = getpass.getpass("Enter MySQL password: ")

        # Validate connection
        if not self._test_connection():
            print("Failed to connect to database. Please check your credentials.")
            sys.exit(1)

    def _test_connection(self) -> bool:
        """
        Test database connection without selecting a specific database.

        Attempts to establish a connection to the MySQL server using provided credentials
        but does not specify a database name. This verifies server accessibility and
        authentication without requiring the target database to exist.

        Returns:
            bool: True if connection successful, False otherwise.

        Logs:
            ERROR: Details of connection failure for troubleshooting.
        """
        try:
            # Attempt connection without database selection
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                port=self.port,
                charset=self.charset,
                connect_timeout=10
            )
            connection.close()
            return True
        except pymysql.Error as err:
            logger.error(f"Database connection test failed: {err}")
            return False

    def get_connection_params(self) -> Dict[str, Any]:
        """
        Get complete connection parameters dictionary for pymysql.connect().

        Returns a dictionary containing all necessary parameters for establishing
        a MySQL database connection, including timeout settings for robust operation.

        Returns:
            Dict[str, Any]: Dictionary with connection parameters including:
                - host: Server hostname
                - user: Database username
                - password: User password
                - database: Target database name
                - port: Server port
                - charset: Character encoding
                - autocommit: Transaction auto-commit setting
                - connect_timeout: Connection establishment timeout
                - read_timeout: Read operation timeout
                - write_timeout: Write operation timeout
        """
        return {
            'host': self.host,
            'user': self.user,
            'password': self.password,
            'database': self.database,
            'port': self.port,
            'charset': self.charset,
            'autocommit': False,
            'connect_timeout': 10,
            'read_timeout': 30,
            'write_timeout': 30
        }

class SchoolManagementSystem:
    """
    School Management System Core Class

    This is the main orchestration class for the comprehensive school management application.
    It manages the complete lifecycle of the application including database initialization,
    user authentication, role-based access control, and provides specialized dashboards
    for different user roles within the educational institution.

    The system implements a multi-role architecture supporting:
    - Administrators: Full system management and configuration
    - Teachers: Student management, attendance, and teaching assignments
    - Students: Personal profile and attendance viewing
    - Principals: Read-only access to all school data
    - Academic Coordinators: Curriculum and subject management
    - Admission Department: Student enrollment and status tracking
    - System Administrators: Technical maintenance and database operations

    Key Capabilities:
    - Secure user authentication with role-based permissions
    - Student enrollment and profile management
    - Teacher hiring and assignment management
    - Attendance tracking for both students and teachers
    - Timetable creation and management with break periods
    - Subject assignment and class management
    - Status management (active, suspended, removed) for users
    - Comprehensive reporting and data analytics
    - Database schema versioning and migration support

    Security Features:
    - Password hashing using SHA-256
    - Role-based access control with granular permissions
    - Secure credential management with environment variable support
    - Transaction-based database operations for data integrity

    Attributes:
        db_config (DatabaseConfig): Instance of DatabaseConfig for connection management.
        connection (pymysql.Connection): Active MySQL database connection object.
        current_user (Optional[dict]): Information about the currently logged-in user.
        current_role (Optional[str]): Current user's role identifier.

    Methods:
        __init__(): Initializes the system with database setup and configuration.
        connect_db(): Establishes and manages database connection with retry logic.
        create_database(): Creates the target database if it doesn't exist.
        create_tables(): Initializes all database tables and default data.
        login(): Handles user authentication process.
        logout(): Clears current user session.
        run(): Main application loop managing login and dashboard routing.

    Role-specific Dashboards:
        admin_dashboard(): Administrative control panel with full system access.
        teacher_dashboard(): Teacher-specific functions and student management.
        student_dashboard(): Student profile and attendance viewing.
        principal_dashboard(): Read-only overview of all school data.
        academic_coordinator_dashboard(): Academic planning and curriculum management.
        admission_department_dashboard(): Student admissions and enrollment.
        system_admin_dashboard(): Technical maintenance and database operations.

    Note:
        All database operations are wrapped in try-except blocks with proper
        error handling and logging. The system uses transaction management
        for data consistency in multi-step operations.
    """

    def __init__(self):
        """
        Initialize the School Management System.

        Sets up database configuration, establishes database connection,
        and creates necessary database tables and default admin user.
        """
        self.db_config = DatabaseConfig()
        self.connection = None
        self.current_user = None
        self.current_role = None
        self.connect_db()
        self.create_tables()
    
    def connect_db(self):
        """
        Establish connection to MySQL database with robust error handling and retry logic.

        Attempts to connect to the specified database with automatic database creation
        if it doesn't exist. Implements retry mechanism for transient connection issues
        and handles specific MySQL error codes appropriately.

        Raises:
            SystemExit: If connection cannot be established after retries.
        """
        max_retries = 3  # Maximum number of connection attempts
        retry_count = 0  # Current retry attempt counter

        while retry_count < max_retries:
            try:
                # First try to connect to the specific database
                self.connection = pymysql.connect(**self.db_config.get_connection_params())
                logger.info("Connected to database successfully!")
                return
            except pymysql.err.OperationalError as err:
                error_code = err.args[0]  # Extract MySQL error code
                if error_code == 1049:  # Unknown database error
                    logger.warning(f"Database '{self.db_config.database}' does not exist. Attempting to create...")
                    if self.create_database():
                        retry_count += 1  # Increment retry after successful database creation
                        continue  # Retry connection with newly created database
                    else:
                        logger.error("Failed to create database")
                        break  # Exit retry loop on creation failure
                elif error_code == 1045:  # Access denied error
                    logger.error("Access denied. Please check your MySQL credentials.")
                    break  # Fatal error, no retry
                elif error_code == 2003:  # Cannot connect to MySQL server
                    logger.error("Can't connect to MySQL server. Please ensure MySQL is running.")
                    break  # Fatal error, no retry
                else:
                    logger.error(f"Database connection error: {err}")
                    retry_count += 1  # Increment retry for unknown operational errors
                    if retry_count < max_retries:
                        logger.info(f"Retrying connection... (attempt {retry_count + 1}/{max_retries})")
                        continue
            except pymysql.Error as err:
                logger.error(f"Unexpected database error: {err}")
                retry_count += 1  # Increment retry for general pymysql errors
                if retry_count < max_retries:
                    logger.info(f"Retrying connection... (attempt {retry_count + 1}/{max_retries})")
                    continue
            except Exception as err:
                logger.error(f"Unexpected error during database connection: {err}")
                break  # Fatal error for non-database exceptions

        logger.error("Failed to establish database connection after multiple attempts")
        sys.exit(1)  # Terminate program on connection failure
    
    def create_database(self) -> bool:
        """
        Create the target database if it doesn't exist.

        Establishes a connection without specifying a database, creates the database
        with proper UTF-8 character set and collation, then reconnects to the new database.

        Returns:
            bool: True if database creation and reconnection successful, False otherwise.

        Logs:
            INFO: Successful database creation.
            ERROR: Details of creation or reconnection failures.
        """
        try:
            # Connect without specifying database to create it
            temp_config = self.db_config.get_connection_params()
            temp_config.pop('database', None)  # Remove database parameter for creation

            connection = pymysql.connect(**temp_config)
            cursor = connection.cursor()

            # Create database with proper charset and collation for Unicode support
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{self.db_config.database}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            cursor.close()
            connection.close()

            logger.info(f"Database '{self.db_config.database}' created successfully!")

            # Now reconnect to the newly created database
            self.connection = pymysql.connect(**self.db_config.get_connection_params())
            return True

        except pymysql.Error as err:
            logger.error(f"Error creating database: {err}")
            return False
        except Exception as err:
            logger.error(f"Unexpected error creating database: {err}")
            return False
    
    def _get_schema_version(self) -> Optional[int]:
        """
        Retrieve the current database schema version.

        Queries the schema_version table to get the latest version number.
        Returns None if the table doesn't exist or is empty.

        Returns:
            Optional[int]: Current schema version number, or None if not available.

        Note:
            Silently returns None if schema_version table doesn't exist yet
            (during initial setup).
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT version FROM schema_version ORDER BY version DESC LIMIT 1")
            result = cursor.fetchone()
            cursor.close()
            return result[0] if result else None
        except pymysql.Error:
            # Schema version table doesn't exist yet (expected during initial setup)
            return None

    def _update_schema_version(self, version: int):
        """
        Update the database schema version number.

        Args:
            version (int): New schema version to set.

        Logs:
            ERROR: If schema version update fails.
        """
        try:
            cursor = self.connection.cursor()
            cursor.execute("UPDATE schema_version SET version = %s", (version,))
            cursor.close()
        except pymysql.Error as err:
            logger.error(f"Failed to update schema version: {err}")

    def hash_password(self, password: str) -> str:
        """
        Hash a password using SHA-256 for secure storage.

        Uses SHA-256 hashing algorithm to create a secure hash of the password.
        Note: In production, consider using salted hashing with libraries like bcrypt.

        Args:
            password (str): Plain text password to hash.

        Returns:
            str: Hexadecimal string representation of the password hash.
        """
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_tables(self):
        """
        Create all necessary database tables with schema versioning.

        Checks current schema version and creates tables only if they don't exist.
        Initializes default admin user. Uses transactional approach for data integrity.

        The system uses schema versioning to track database structure changes.
        Currently supports version 1 schema with all core tables.
        """
        cursor = self.connection.cursor()

        # Check database schema version for potential future migrations
        schema_version = self._get_schema_version()

        logger.info(f"Current database schema version: {schema_version}")

        # Create schema version table if it doesn't exist (required for versioning)
        try:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS schema_version (
                version INT PRIMARY KEY DEFAULT 1,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
            """)
        except pymysql.Error as err:
            logger.error(f"Failed to create schema_version table: {err}")
            return

        # Initialize schema version if empty (first-time setup)
        if schema_version is None:
            try:
                cursor.execute("INSERT INTO schema_version (version) VALUES (1)")
                schema_version = 1
                logger.info("Initialized schema version to 1")
            except pymysql.Error as err:
                logger.error(f"Failed to initialize schema version: {err}")
                return

        # List of all database tables with their CREATE statements
        # Each table includes proper foreign key constraints and indexes
        tables = [
            # Users table: Stores all system users with authentication details
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('admin', 'principal', 'teacher', 'student', 'system_admin', 'academic_coordinator', 'admission_department') NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            # Teachers table: Extended profile information for teaching staff
            """
            CREATE TABLE IF NOT EXISTS teachers (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                name VARCHAR(100) NOT NULL,
                age INT,
                dob DATE,
                highest_qualifications TEXT,
                teaching_subject VARCHAR(100),
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            # Teaching records table: Historical employment records for teachers
            """
            CREATE TABLE IF NOT EXISTS teaching_records (
                id INT AUTO_INCREMENT PRIMARY KEY,
                teacher_id INT,
                school_name VARCHAR(255),
                duration VARCHAR(100),
                position VARCHAR(100),
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
            )
            """,
            # Classes table: Academic class divisions (e.g., 12th-A, 11th-B)
            """
            CREATE TABLE IF NOT EXISTS classes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                class_name VARCHAR(50) NOT NULL,
                section VARCHAR(10) NOT NULL,
                UNIQUE KEY unique_class_section (class_name, section)
            )
            """,
            # Subjects table: Academic subjects offered in specific classes
            """
            CREATE TABLE IF NOT EXISTS subjects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                subject_name VARCHAR(100) NOT NULL,
                class_id INT,
                teacher_id INT,
                FOREIGN KEY (class_id) REFERENCES classes(id) ON DELETE CASCADE,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE SET NULL
            )
            """,
            # Students table: Detailed student information and enrollment data
            """
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
            )
            """,
            # Student subjects table: Many-to-many relationship between students and subjects
            """
            CREATE TABLE IF NOT EXISTS student_subjects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                subject_id INT,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subjects(id) ON DELETE CASCADE
            )
            """,
            # Timetable table: Daily schedule for classes with subject and teacher assignments
            """
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
            )
            """,
            # Student attendance table: Daily attendance records for students
            """
            CREATE TABLE IF NOT EXISTS student_attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                date DATE NOT NULL,
                status ENUM('present', 'absent') NOT NULL,
                recorded_by INT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (recorded_by) REFERENCES users(id) ON DELETE SET NULL
            )
            """,
            # Teacher attendance table: Daily attendance records for teachers
            """
            CREATE TABLE IF NOT EXISTS teacher_attendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                teacher_id INT,
                date DATE NOT NULL,
                status ENUM('present', 'absent') NOT NULL,
                recorded_by INT,
                recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
                FOREIGN KEY (recorded_by) REFERENCES users(id) ON DELETE CASCADE
            )
            """,
            # Teacher privileges table: Granular permissions for teacher actions
            """
            CREATE TABLE IF NOT EXISTS teacher_privileges (
                id INT AUTO_INCREMENT PRIMARY KEY,
                teacher_id INT,
                can_edit_students BOOLEAN DEFAULT FALSE,
                can_delete_students BOOLEAN DEFAULT FALSE,
                can_suspend_students BOOLEAN DEFAULT FALSE,
                can_edit_subjects BOOLEAN DEFAULT FALSE,
                can_delete_subjects BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE
            )
            """,
            # Student status table: Suspension and removal tracking for students
            """
            CREATE TABLE IF NOT EXISTS student_status (
                id INT AUTO_INCREMENT PRIMARY KEY,
                student_id INT,
                status ENUM('active', 'suspended', 'removed') DEFAULT 'active',
                suspension_reason TEXT,
                suspended_by INT,
                suspended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
                FOREIGN KEY (suspended_by) REFERENCES users(id) ON DELETE SET NULL
            )
            """,
            # Teacher status table: Suspension and removal tracking for teachers
            """
            CREATE TABLE IF NOT EXISTS teacher_status (
                 id INT AUTO_INCREMENT PRIMARY KEY,
                 teacher_id INT,
                 status ENUM('active', 'suspended', 'removed') DEFAULT 'active',
                 suspension_reason TEXT,
                 suspended_by INT,
                 suspended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                 FOREIGN KEY (teacher_id) REFERENCES teachers(id) ON DELETE CASCADE,
                 FOREIGN KEY (suspended_by) REFERENCES users(id) ON DELETE SET NULL
             )
             """,
            """
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
            )
            """
        ]
        
        try:
            for table in tables:
                cursor.execute(table)
            self.connection.commit()

            # Create default admin user if not exists
            cursor.execute("SELECT * FROM users WHERE username = 'admin'")
            if not cursor.fetchone():
                admin_password = self.hash_password('admin123')
                cursor.execute(
                    "INSERT INTO users (username, password, role) VALUES (%s, %s, 'admin')",
                    ('admin', admin_password)
                )
                self.connection.commit()
                print("Default admin created - Username: admin, Password: admin123")

        except pymysql.Error as err:
            print(f"Error creating tables: {err}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def login(self):
        """
        Authenticate user credentials and establish session.

        Prompts for username and password, verifies against database records,
        and performs additional checks for suspended/removed teachers.
        Updates instance variables current_user and current_role on success.

        Returns:
            bool: True if authentication successful and session established, False otherwise.

        Note:
            Passwords are hashed using SHA-256 for secure comparison.
            Teacher accounts may have suspension/removal status that prevents login.
        """
        print("\n" + "="*50)
        print("        SCHOOL MANAGEMENT SYSTEM LOGIN")
        print("="*50)
        
        username = input("Username: ").strip()
        password = getpass.getpass("Password: ").strip()
        
        if not username or not password:
            print("Username and password are required!")
            return False
        
        hashed_password = self.hash_password(password)
        
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        try:
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, hashed_password))
            user = cursor.fetchone()
            
            if user:
                # Check if teacher is suspended (only for teacher role)
                if user['role'] == 'teacher':
                    cursor.execute("SELECT status, suspension_reason FROM teacher_status WHERE teacher_id = (SELECT id FROM teachers WHERE user_id = %s)", (user['id'],))
                    teacher_status = cursor.fetchone()
                    if teacher_status and teacher_status['status'] == 'suspended':
                        print("Your account is suspended.")
                        if teacher_status['suspension_reason']:
                            print(f"Reason: {teacher_status['suspension_reason']}")
                        print("Please contact the administrator to resolve this issue.")
                        return False
                    elif teacher_status and teacher_status['status'] == 'removed':
                        print("Your account has been removed.")
                        print("Please contact the administrator for more information.")
                        return False

                self.current_user = user
                self.current_role = user['role']
                print(f"\nWelcome {username}! Role: {self.current_role.title()}")
                return True
            else:
                print("Invalid credentials!")
                return False
        except pymysql.Error as err:
            print(f"Database error: {err}")
            return False
        finally:
            cursor.close()
    
    def logout(self):
        """
        Clear the current user session.

        Resets the current_user and current_role instance variables to None,
        effectively ending the user's authenticated session. Displays a logout message.
        """
        print(f"\nGoodbye {self.current_user['username']}!")
        self.current_user = None
        self.current_role = None
    
    def admin_dashboard(self):
        """
        Display and handle the administration dashboard menu.

        Presents a comprehensive menu system for administrative operations including
        user creation/management, class and subject management, attendance tracking,
        timetable creation, and various reporting and maintenance functions.
        Processes user input in a continuous loop until the user chooses to logout.

        Menu Options:
            1-4: User creation (Teacher, Class, Subject, Student)
            5-8: Attendance and timetable management
            9-16: Viewing and management functions
            17-22: Advanced admin functions (status management, assignments, etc.)
            23-26: Special user creation and logout

        Note:
            All operations require appropriate database permissions and may involve
            transaction-based updates for data integrity.
        """
        while True:
            print("\n" + "="*50)
            print("            ADMIN DASHBOARD")
            print("="*50)
            print("1.  Create Teacher")
            print("2.  Create Class")
            print("3.  Create Subject")
            print("4.  Create Student")
            print("5.  Create Timetable")
            print("6.  View Attendance Records")
            print("7.  Mark Teacher Attendance")
            print("8.  View All Teachers")
            print("9.  View All Students")
            print("10. View All Classes")
            print("11. Manage Teacher Privileges")
            print("12. Assign Teachers to Classes")
            print("13. Edit Teacher Assignments")
            print("14. Manage Student Status")
            print("15. Manage Teacher Status")
            print("16. Manage Subjects")
            print("17. Edit Student Class Assignment")
            print("18. Edit User Details")
            print("19. Database Maintenance")
            print("20. View Student Attendance History")
            print("21. Create Principal")
            print("22. Create Academic Coordinator")
            print("23. Create Admission Department User")
            print("24. View User Credentials")
            print("25. Mark Student Attendance")
            print("26. Logout")

            choice = input("\nEnter your choice (1-26): ").strip()

            if choice == '1':
                self.create_teacher()
            elif choice == '2':
                self.create_class()
            elif choice == '3':
                self.create_subject()
            elif choice == '4':
                self.create_student()
            elif choice == '5':
                self.create_timetable()
            elif choice == '6':
                self.view_attendance_records()
            elif choice == '7':
                self.mark_teacher_attendance()
            elif choice == '8':
                self.view_all_teachers()
            elif choice == '9':
                self.view_all_students()
            elif choice == '10':
                self.view_all_classes()
            elif choice == '11':
                self.manage_teacher_privileges()
            elif choice == '12':
                self.assign_teachers_to_classes()
            elif choice == '13':
                self.edit_teacher_assignments()
            elif choice == '14':
                self.manage_student_status()
            elif choice == '15':
                self.manage_teacher_status()
            elif choice == '16':
                self.manage_subjects()
            elif choice == '17':
                self.edit_student_class_assignment()
            elif choice == '18':
                self.edit_user_details()
            elif choice == '19':
                self.database_maintenance()
            elif choice == '20':
                self.view_student_attendance_history()
            elif choice == '21':
                self.create_principal()
            elif choice == '22':
                self.create_academic_coordinator()
            elif choice == '23':
                self.create_admission_department()
            elif choice == '24':
                self.view_user_credentials()
            elif choice == '25':
                self.mark_student_attendance_admin()
            elif choice == '26':
                self.logout()
                break
            else:
                print("Invalid choice! Please try again.")

    def view_user_credentials(self):
        """Admin: View all user usernames and passwords"""
        print("\n" + "="*50)
        print("        VIEW USER CREDENTIALS")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT u.id, u.username, u.role,
                   CASE WHEN u.role = 'student' THEN s.name
                        WHEN u.role IN ('teacher', 'principal', 'academic_coordinator', 'admission_department') THEN t.name
                        ELSE 'N/A' END as name,
                   CASE WHEN u.role = 'student' THEN CONCAT(c.class_name, '-', c.section)
                        ELSE 'N/A' END as class_info
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            LEFT JOIN teachers t ON u.id = t.user_id
            LEFT JOIN classes c ON s.class_id = c.id
            ORDER BY u.role, u.username
            """)

            users = cursor.fetchall()

            if not users:
                print("No users found.")
                return

            print("\nAll User Credentials:")
            print("-" * 100)
            print(f"{'ID':<3} {'Username':<20} {'Role':<20} {'Name':<25} {'Class':<10}")
            print("-" * 100)

            for user in users:
                name = user['name'] or 'N/A'
                class_info = user['class_info'] or 'N/A'
                print(f"{user['id']:<3} {user['username']:<20} {user['role']:<20} {name[:24]:<25} {class_info:<10}")

            print("-" * 100)
            print(f"\nTotal users: {len(users)}")
            print("\nNOTE: All user passwords are hashed. Default passwords:")
            print("  - Admin: admin123")
            print("  - Teachers: teacher123")
            print("  - Students: student123 (or as set by admin)")
            print("  - Other roles: role123 (e.g., principal123)")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def mark_student_attendance_admin(self):
        """Admin: Mark attendance for students in any class"""
        print("\n" + "="*50)
        print("    ADMIN: MARK STUDENT ATTENDANCE")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show available classes
            cursor.execute("SELECT * FROM classes ORDER BY class_name, section")
            classes = cursor.fetchall()

            if not classes:
                print("No classes available.")
                return

            print("\nAvailable Classes:")
            for cls in classes:
                print(f"{cls['id']}. {cls['class_name']} - Section {cls['section']}")

            class_id = int(input("\nSelect Class ID: "))

            # Verify class exists
            cursor.execute("SELECT class_name, section FROM classes WHERE id = %s", (class_id,))
            class_info = cursor.fetchone()
            if not class_info:
                print("Class not found!")
                return

            attendance_date = input("Date (YYYY-MM-DD) [Today]: ").strip()
            if not attendance_date:
                attendance_date = date.today().isoformat()

            # Get all students from the selected class (regardless of status, but show status)
            cursor.execute("""
            SELECT s.id, s.name, s.admission_number,
                   CASE WHEN ss.status IS NULL THEN 'active' ELSE ss.status END as status
            FROM students s
            LEFT JOIN student_status ss ON s.id = ss.student_id
            WHERE s.class_id = %s
            ORDER BY s.name
            """, (class_id,))

            students = cursor.fetchall()

            if not students:
                print("No students in this class.")
                return

            print(f"\nMarking attendance for {class_info['class_name']}-{class_info['section']} on {attendance_date}")
            print("Status: A=Absent, P=Present, S=Suspended, R=Removed")
            print("Enter 'P' for Present, 'A' for Absent, or press Enter for Absent")
            print("-" * 70)

            marked_count = 0
            for student in students:
                status_display = student['status'][0].upper() if len(student['status']) > 0 else 'A'
                status_input = input(f"{student['name']} ({student['admission_number']}) [{status_display}]: ").strip().upper()

                if status_input == 'P':
                    final_status = 'present'
                elif status_input == 'A':
                    final_status = 'absent'
                else:
                    # Default to absent if invalid input
                    final_status = 'absent'

                # Check if attendance already exists
                cursor.execute(
                    "SELECT id FROM student_attendance WHERE student_id = %s AND date = %s",
                    (student['id'], attendance_date)
                )
                existing = cursor.fetchone()

                if existing:
                    # Update existing
                    update_query = """
                    UPDATE student_attendance
                    SET status = %s, recorded_by = %s, recorded_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """
                    cursor.execute(update_query, (final_status, self.current_user['id'], existing['id']))
                else:
                    # Insert new
                    insert_query = """
                    INSERT INTO student_attendance (student_id, date, status, recorded_by)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (student['id'], attendance_date, final_status, self.current_user['id']))

                marked_count += 1

            self.connection.commit()
            print(f"\n✓ Attendance marked successfully for {marked_count} students in {class_info['class_name']}-{class_info['section']}!")
            print("✓ Attendance results are now reflected in teacher and student profiles.")

        except ValueError:
            print("Invalid class ID!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def create_teacher(self):
        """Create a new teacher"""
        print("\n" + "="*50)
        print("            CREATE NEW TEACHER")
        print("="*50)

        try:
            name = input("Full Name: ").strip()
            if not name:
                print("Name is required!")
                return

            # Get date of birth and calculate age
            while True:
                dob_input = input("Date of Birth (YYYY-MM-DD): ").strip()
                try:
                    dob = datetime.strptime(dob_input, '%Y-%m-%d').date()
                    today = date.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    break
                except ValueError:
                    print("Invalid date format! Please enter in YYYY-MM-DD format.")

            qualifications = input("Highest Qualifications: ").strip()
            subject = input("Teaching Subject: ").strip()

            # Get username and password from admin
            while True:
                username = input("Username: ").strip()
                if not username:
                    print("Username is required!")
                    continue
                # Check if username already exists
                cursor = self.connection.cursor()
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    print("Username already exists! Please choose a different username.")
                    cursor.close()
                    continue
                cursor.close()
                break

            password = input("Password: ").strip()
            if not password:
                print("Password is required!")
                return

            cursor = self.connection.cursor()

            # Create user account
            hashed_password = self.hash_password(password)

            user_query = "INSERT INTO users (username, password, role) VALUES (%s, %s, 'teacher')"
            cursor.execute(user_query, (username, hashed_password))
            user_id = cursor.lastrowid

            # Create teacher profile
            teacher_query = """
            INSERT INTO teachers (user_id, name, age, dob, highest_qualifications, teaching_subject)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(teacher_query, (user_id, name, age, dob, qualifications, subject))
            teacher_id = cursor.lastrowid

            # Add teaching records
            print("\nAdd Teaching Records (Leave school name empty to finish):")
            record_count = 0
            while True:
                school = input("\nSchool Name: ").strip()
                if not school:
                    break
                duration = input("Duration (e.g., 2018-2020): ").strip()
                position = input("Position: ").strip()

                record_query = """
                INSERT INTO teaching_records (teacher_id, school_name, duration, position)
                VALUES (%s, %s, %s, %s)
                """
                cursor.execute(record_query, (teacher_id, school, duration, position))
                record_count += 1
                print("Record added!")

            self.connection.commit()
            print(f"\nTeacher created successfully!")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"Age: {age} (calculated from DOB)")
            print(f"Teaching records added: {record_count}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def create_principal(self):
        """Create a new principal"""
        print("\n" + "="*50)
        print("            CREATE NEW PRINCIPAL")
        print("="*50)

        try:
            name = input("Full Name: ").strip()
            if not name:
                print("Name is required!")
                return

            # Get date of birth and calculate age
            while True:
                dob_input = input("Date of Birth (YYYY-MM-DD): ").strip()
                try:
                    dob = datetime.strptime(dob_input, '%Y-%m-%d').date()
                    today = date.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    break
                except ValueError:
                    print("Invalid date format! Please enter in YYYY-MM-DD format.")

            qualifications = input("Highest Qualifications: ").strip()
            experience = input("Years of Experience: ").strip()

            # Get username and password from admin
            while True:
                username = input("Username: ").strip()
                if not username:
                    print("Username is required!")
                    continue
                # Check if username already exists
                cursor = self.connection.cursor()
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    print("Username already exists! Please choose a different username.")
                    cursor.close()
                    continue
                cursor.close()
                break

            password = input("Password: ").strip()
            if not password:
                print("Password is required!")
                return

            cursor = self.connection.cursor()

            # Create user account
            hashed_password = self.hash_password(password)

            user_query = "INSERT INTO users (username, password, role) VALUES (%s, %s, 'principal')"
            cursor.execute(user_query, (username, hashed_password))
            user_id = cursor.lastrowid

            # Create principal profile (using teachers table for now, as it has similar fields)
            principal_query = """
            INSERT INTO teachers (user_id, name, age, dob, highest_qualifications, teaching_subject)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(principal_query, (user_id, name, age, dob, qualifications, experience))

            self.connection.commit()
            print(f"\nPrincipal created successfully!")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"Age: {age} (calculated from DOB)")

        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def create_academic_coordinator(self):
        """Create a new academic coordinator"""
        print("\n" + "="*50)
        print("        CREATE NEW ACADEMIC COORDINATOR")
        print("="*50)

        try:
            name = input("Full Name: ").strip()
            if not name:
                print("Name is required!")
                return

            # Get date of birth and calculate age
            while True:
                dob_input = input("Date of Birth (YYYY-MM-DD): ").strip()
                try:
                    dob = datetime.strptime(dob_input, '%Y-%m-%d').date()
                    today = date.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    break
                except ValueError:
                    print("Invalid date format! Please enter in YYYY-MM-DD format.")

            qualifications = input("Highest Qualifications: ").strip()
            department = input("Department/Specialization: ").strip()

            # Get username and password from admin
            while True:
                username = input("Username: ").strip()
                if not username:
                    print("Username is required!")
                    continue
                # Check if username already exists
                cursor = self.connection.cursor()
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    print("Username already exists! Please choose a different username.")
                    cursor.close()
                    continue
                cursor.close()
                break

            password = input("Password: ").strip()
            if not password:
                print("Password is required!")
                return

            cursor = self.connection.cursor()

            # Create user account
            hashed_password = self.hash_password(password)

            user_query = "INSERT INTO users (username, password, role) VALUES (%s, %s, 'academic_coordinator')"
            cursor.execute(user_query, (username, hashed_password))
            user_id = cursor.lastrowid

            # Create academic coordinator profile (using teachers table for now)
            coordinator_query = """
            INSERT INTO teachers (user_id, name, age, dob, highest_qualifications, teaching_subject)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(coordinator_query, (user_id, name, age, dob, qualifications, department))

            self.connection.commit()
            print(f"\nAcademic Coordinator created successfully!")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"Age: {age} (calculated from DOB)")

        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def create_admission_department(self):
        """Create a new admission department user"""
        print("\n" + "="*50)
        print("       CREATE NEW ADMISSION DEPARTMENT USER")
        print("="*50)

        try:
            name = input("Full Name: ").strip()
            if not name:
                print("Name is required!")
                return

            # Get date of birth and calculate age
            while True:
                dob_input = input("Date of Birth (YYYY-MM-DD): ").strip()
                try:
                    dob = datetime.strptime(dob_input, '%Y-%m-%d').date()
                    today = date.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    break
                except ValueError:
                    print("Invalid date format! Please enter in YYYY-MM-DD format.")

            qualifications = input("Highest Qualifications: ").strip()
            role_description = input("Role Description: ").strip()

            # Get username and password from admin
            while True:
                username = input("Username: ").strip()
                if not username:
                    print("Username is required!")
                    continue
                # Check if username already exists
                cursor = self.connection.cursor()
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    print("Username already exists! Please choose a different username.")
                    cursor.close()
                    continue
                cursor.close()
                break

            password = input("Password: ").strip()
            if not password:
                print("Password is required!")
                return

            cursor = self.connection.cursor()

            # Create user account
            hashed_password = self.hash_password(password)

            user_query = "INSERT INTO users (username, password, role) VALUES (%s, %s, 'admission_department')"
            cursor.execute(user_query, (username, hashed_password))
            user_id = cursor.lastrowid

            # Create admission department profile (using teachers table for now)
            admission_query = """
            INSERT INTO teachers (user_id, name, age, dob, highest_qualifications, teaching_subject)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(admission_query, (user_id, name, age, dob, qualifications, role_description))

            self.connection.commit()
            print(f"\nAdmission Department User created successfully!")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"Age: {age} (calculated from DOB)")

        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def create_class(self):
        """Create a new class"""
        print("\n" + "="*50)
        print("            CREATE NEW CLASS")
        print("="*50)
        
        class_name = input("Class Name (e.g., 12th, 11th): ").strip()
        section = input("Section (e.g., A, B): ").strip().upper()
        
        if not class_name or not section:
            print("Class name and section are required!")
            return
        
        cursor = self.connection.cursor()
        try:
            query = "INSERT INTO classes (class_name, section) VALUES (%s, %s)"
            cursor.execute(query, (class_name, section))
            self.connection.commit()
            print(f"Class {class_name}-{section} created successfully!")
        except pymysql.IntegrityError:
            print("Class with this name and section already exists!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def create_subject(self):
        """Create a new subject and assign teacher"""
        print("\n" + "="*50)
        print("            CREATE NEW SUBJECT")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show available classes
            cursor.execute("SELECT * FROM classes ORDER BY class_name, section")
            classes = cursor.fetchall()

            if not classes:
                print("No classes available. Please create a class first.")
                return

            print("\nAvailable Classes:")
            for cls in classes:
                print(f"{cls['id']}. {cls['class_name']} - Section {cls['section']}")

            class_id = int(input("\nSelect Class ID: "))

            # Verify class exists
            cursor.execute("SELECT class_name, section FROM classes WHERE id = %s", (class_id,))
            class_info = cursor.fetchone()
            if not class_info:
                print("Class not found!")
                return

            # Show available teachers
            cursor.execute("SELECT * FROM teachers ORDER BY name")
            teachers = cursor.fetchall()

            if not teachers:
                print("No teachers available. Please create a teacher first.")
                return

            print("\nAvailable Teachers:")
            for teacher in teachers:
                print(f"{teacher['id']}. {teacher['name']} - {teacher['teaching_subject']}")

            teacher_id = int(input("Select Teacher ID: "))
            subject_name = input("Subject Name: ").strip()

            if not subject_name:
                print("Subject name is required!")
                return

            # Create subject
            query = """
            INSERT INTO subjects (subject_name, class_id, teacher_id)
            VALUES (%s, %s, %s)
            """
            cursor.execute(query, (subject_name, class_id, teacher_id))
            subject_id = cursor.lastrowid

            # Create teacher assignment record
            cursor.execute("""
            INSERT INTO teacher_assignments (teacher_id, class_id, subject_id, assigned_by)
            VALUES (%s, %s, %s, %s)
            """, (teacher_id, class_id, subject_id, self.current_user['id']))

            self.connection.commit()
            print("✓ Subject created and teacher assigned successfully!")

        except ValueError:
            print("Invalid input! Please enter numbers for IDs.")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def create_student(self):
        """Create a new student assigned to specific class and section"""
        print("\n" + "="*50)
        print("            CREATE NEW STUDENT")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            admission_no = input("Admission Number: ").strip()
            if not admission_no:
                print("Admission number is required!")
                return

            name = input("Full Name: ").strip()
            if not name:
                print("Name is required!")
                return

            # Get date of birth and calculate age
            while True:
                dob_input = input("Date of Birth (YYYY-MM-DD): ").strip()
                try:
                    dob = datetime.strptime(dob_input, '%Y-%m-%d').date()
                    today = date.today()
                    age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
                    break
                except ValueError:
                    print("Invalid date format! Please enter in YYYY-MM-DD format.")

            previous_school = input("Previous School: ").strip()

            # Show available class names first
            cursor.execute("SELECT DISTINCT class_name FROM classes ORDER BY class_name")
            class_names = cursor.fetchall()

            if not class_names:
                print("No classes available. Please create a class first.")
                return

            print("\nAvailable Class Names:")
            for i, cls in enumerate(class_names, 1):
                print(f"{i}. {cls['class_name']}")

            class_choice = int(input("\nSelect Class Name (number): "))

            if class_choice < 1 or class_choice > len(class_names):
                print("Invalid class selection!")
                return

            selected_class_name = class_names[class_choice - 1]['class_name']

            # Show sections for selected class
            cursor.execute("SELECT id, section FROM classes WHERE class_name = %s ORDER BY section", (selected_class_name,))
            sections = cursor.fetchall()

            if not sections:
                print("No sections found for this class.")
                return

            print(f"\nAvailable Sections for {selected_class_name}:")
            for section in sections:
                print(f"{section['id']}. Section {section['section']}")

            class_id = int(input(f"\nSelect Section ID for {selected_class_name}: "))

            # Verify the class_id belongs to the selected class
            cursor.execute("SELECT id, class_name, section FROM classes WHERE id = %s", (class_id,))
            class_info = cursor.fetchone()
            if not class_info or class_info['class_name'] != selected_class_name:
                print("Invalid section selection!")
                return

            print(f"\nAssigning student to: {class_info['class_name']} - Section {class_info['section']}")

            # Parent details
            father_name = input("Father's Name: ").strip()
            mother_name = input("Mother's Name: ").strip()
            father_occupation = input("Father's Occupation: ").strip()
            mother_occupation = input("Mother's Occupation: ").strip()
            contact = input("Contact Number: ").strip()
            emergency_contact = input("Emergency Contact: ").strip()

            # Get username and password from admin
            while True:
                username = input("Username: ").strip()
                if not username:
                    print("Username is required!")
                    continue
                # Check if username already exists
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if cursor.fetchone():
                    print("Username already exists! Please choose a different username.")
                    continue
                break

            password = input("Password: ").strip()
            if not password:
                print("Password is required!")
                return

            # Create user account
            hashed_password = self.hash_password(password)

            user_query = "INSERT INTO users (username, password, role) VALUES (%s, %s, 'student')"
            cursor.execute(user_query, (username, hashed_password))
            user_id = cursor.lastrowid

            # Create student profile
            student_query = """
            INSERT INTO students (user_id, admission_number, name, age, dob, class_id,
            previous_school, father_name, mother_name, father_occupation, mother_occupation,
            contact_number, emergency_contact)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(student_query, (user_id, admission_no, name, age, dob, class_id,
                                         previous_school, father_name, mother_name,
                                         father_occupation, mother_occupation, contact, emergency_contact))
            student_id = cursor.lastrowid

            # Auto-assign subjects from the selected class-section
            cursor.execute("SELECT id, subject_name FROM subjects WHERE class_id = %s", (class_id,))
            subjects = cursor.fetchall()

            if subjects:
                for subject in subjects:
                    cursor.execute("""
                    INSERT INTO student_subjects (student_id, subject_id)
                    VALUES (%s, %s)
                    """, (student_id, subject['id']))
                print(f"✓ Auto-assigned {len(subjects)} subjects to student")

            self.connection.commit()
            print(f"\n✓ Student created successfully!")
            print(f"Username: {username}")
            print(f"Password: {password}")
            print(f"Age: {age} (calculated from DOB)")
            print(f"Assigned to: {class_info['class_name']} - Section {class_info['section']}")
            print(f"Auto-assigned subjects: {len(subjects) if subjects else 0}")

        except pymysql.IntegrityError:
            print("Admission number already exists!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def create_timetable(self):
        """Create timetable for a class with break times and teacher assignments"""
        print("\n" + "="*50)
        print("            CREATE TIMETABLE")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show available classes
            cursor.execute("SELECT * FROM classes ORDER BY class_name, section")
            classes = cursor.fetchall()

            if not classes:
                print("No classes available. Please create a class first.")
                return

            print("\nAvailable Classes:")
            for cls in classes:
                print(f"{cls['id']}. {cls['class_name']} - Section {cls['section']}")

            class_id = int(input("\nSelect Class ID: "))

            # Get class info
            cursor.execute("SELECT class_name, section FROM classes WHERE id = %s", (class_id,))
            class_info = cursor.fetchone()

            if not class_info:
                print("Class not found!")
                return

            days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
            lectures = int(input("Number of lectures per day: "))

            # Get break times (optional)
            add_break = input("Add break time? (y/n): ").strip().lower()
            break_start = None
            break_end = None

            if add_break == 'y':
                break_start = input("Break Start Time (HH:MM:SS): ").strip()
                break_end = input("Break End Time (HH:MM:SS): ").strip()

            print(f"\nCreating timetable for {class_info['class_name']}-{class_info['section']}")
            print(f"Lectures per day: {lectures}")
            if break_start and break_end:
                print(f"Break time: {break_start} - {break_end}")

            for day in days:
                print(f"\n--- {day.upper()} ---")
                for lecture in range(1, lectures + 1):
                    print(f"\nLecture {lecture}:")

                    # Check if this is break time
                    is_break = False
                    if break_start and break_end:
                        check_break = input(f"Is Lecture {lecture} a break? (y/n): ").strip().lower()
                        if check_break == 'y':
                            is_break = True

                    if is_break:
                        start_time = break_start
                        end_time = break_end
                        subject_id = None
                        teacher_id = None
                        print("Break period added!")
                    else:
                        start_time = input("Start Time (HH:MM:SS): ").strip()
                        end_time = input("End Time (HH:MM:SS): ").strip()

                        # Show available subjects for this class
                        cursor.execute("""
                        SELECT s.id, s.subject_name, t.name as teacher_name
                        FROM subjects s
                        LEFT JOIN teachers t ON s.teacher_id = t.id
                        WHERE s.class_id = %s
                        """, (class_id,))
                        subjects = cursor.fetchall()

                        if not subjects:
                            print("No subjects available for this class.")
                            continue

                        print("Available Subjects:")
                        for subject in subjects:
                            teacher_name = subject['teacher_name'] if subject['teacher_name'] else "Not assigned"
                            print(f"{subject['id']}. {subject['subject_name']} - {teacher_name}")

                        subject_id = int(input("Select Subject ID: "))

                        # Verify subject exists and get teacher
                        cursor.execute("""
                        SELECT s.subject_name, s.teacher_id, t.name as teacher_name
                        FROM subjects s
                        LEFT JOIN teachers t ON s.teacher_id = t.id
                        WHERE s.id = %s AND s.class_id = %s
                        """, (subject_id, class_id))
                        subject_info = cursor.fetchone()

                        if not subject_info:
                            print("Subject not found for this class!")
                            continue

                        teacher_id = subject_info['teacher_id']
                        print(f"Assigned Teacher: {subject_info['teacher_name'] or 'Not assigned'}")
                        print("Lecture added!")

                    # Insert timetable entry
                    query = """
                    INSERT INTO timetable (class_id, day_of_week, lecture_number,
                    start_time, end_time, subject_id, teacher_id, break_start_time,
                    break_end_time, created_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    cursor.execute(query, (class_id, day.lower(), lecture, start_time,
                                        end_time, subject_id, teacher_id,
                                        break_start if is_break else None,
                                        break_end if is_break else None,
                                        self.current_user['id']))

            self.connection.commit()
            print(f"\n✓ Timetable created successfully for {class_info['class_name']}-{class_info['section']}!")
            print(f"✓ Total lectures: {lectures * len(days)}")
            print(f"✓ Created by: {self.current_user['username']}")

        except ValueError:
            print("Invalid input! Please enter numbers where required.")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def view_attendance_records(self):
        """View attendance records"""
        print("\n" + "="*50)
        print("            ATTENDANCE RECORDS")
        print("="*50)
        print("1. Student Attendance")
        print("2. Teacher Attendance")
        
        choice = input("\nEnter choice (1-2): ").strip()
        
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        
        try:
            if choice == '1':
                cursor.execute("""
                SELECT sa.date, s.name as student_name, c.class_name, c.section,
                       sa.status, u.username as recorded_by
                FROM student_attendance sa
                JOIN students s ON sa.student_id = s.id
                JOIN classes c ON s.class_id = c.id
                LEFT JOIN users u ON sa.recorded_by = u.id
                ORDER BY sa.date DESC, s.name
                LIMIT 50
                """)
                records = cursor.fetchall()
                
                print("\nStudent Attendance Records (Latest 50):")
                print("-" * 80)
                for record in records:
                    print(f"Date: {record['date']} | Student: {record['student_name']} | "
                          f"Class: {record['class_name']}-{record['section']} | "
                          f"Status: {record['status'].upper()} | "
                          f"Recorded by: {record['recorded_by']}")
                
            elif choice == '2':
                cursor.execute("""
                SELECT ta.date, t.name as teacher_name, ta.status, 
                       u.username as recorded_by, ta.recorded_at
                FROM teacher_attendance ta
                JOIN teachers t ON ta.teacher_id = t.id
                JOIN users u ON ta.recorded_by = u.id
                ORDER BY ta.date DESC, t.name
                LIMIT 50
                """)
                records = cursor.fetchall()
                
                print("\nTeacher Attendance Records (Latest 50):")
                print("-" * 80)
                for record in records:
                    print(f"Date: {record['date']} | Teacher: {record['teacher_name']} | "
                          f"Status: {record['status'].upper()} | "
                          f"Recorded by: {record['recorded_by']}")
            else:
                print("Invalid choice!")
                return
                
            print(f"\nTotal records displayed: {len(records)}")
            
        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()
    
    def mark_teacher_attendance(self):
        """Mark attendance for teachers"""
        print("\n" + "="*50)
        print("        MARK TEACHER ATTENDANCE")
        print("="*50)
        
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        
        try:
            # Get all teachers
            cursor.execute("SELECT * FROM teachers ORDER BY name")
            teachers = cursor.fetchall()
            
            if not teachers:
                print("No teachers available.")
                return
            
            attendance_date = input("Date (YYYY-MM-DD) [Today]: ").strip()
            if not attendance_date:
                attendance_date = date.today().isoformat()
            
            print(f"\nMarking attendance for {attendance_date}")
            print("Enter 'P' for Present, 'A' for Absent, or press Enter for Absent")
            print("-" * 60)
            
            for teacher in teachers:
                status = input(f"{teacher['name']} [P/A]: ").strip().upper()
                final_status = 'present' if status == 'P' else 'absent'
                
                # Check if attendance already exists for this date
                cursor.execute(
                    "SELECT id FROM teacher_attendance WHERE teacher_id = %s AND date = %s",
                    (teacher['id'], attendance_date)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing attendance
                    update_query = """
                    UPDATE teacher_attendance 
                    SET status = %s, recorded_by = %s, recorded_at = CURRENT_TIMESTAMP 
                    WHERE id = %s
                    """
                    cursor.execute(update_query, (final_status, self.current_user['id'], existing['id']))
                else:
                    # Insert new attendance
                    insert_query = """
                    INSERT INTO teacher_attendance (teacher_id, date, status, recorded_by)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (teacher['id'], attendance_date, final_status, self.current_user['id']))
            
            self.connection.commit()
            print("\nTeacher attendance marked successfully!")
            
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def view_all_teachers(self):
        """View all teachers"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
            SELECT t.*, COUNT(tr.id) as record_count 
            FROM teachers t 
            LEFT JOIN teaching_records tr ON t.id = tr.teacher_id 
            GROUP BY t.id 
            ORDER BY t.name
            """)
            teachers = cursor.fetchall()
            
            print("\n" + "="*50)
            print("            ALL TEACHERS")
            print("="*50)
            
            for teacher in teachers:
                print(f"\nID: {teacher['id']}")
                print(f"Name: {teacher['name']}")
                print(f"Age: {teacher['age']}")
                print(f"Subject: {teacher['teaching_subject']}")
                print(f"Qualifications: {teacher['highest_qualifications']}")
                print(f"Teaching Records: {teacher['record_count']}")
                print("-" * 40)
            
            print(f"\nTotal Teachers: {len(teachers)}")
            
        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()
    
    def view_all_students(self):
        """View all students grouped by class and section"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT s.*, c.class_name, c.section
            FROM students s
            JOIN classes c ON s.class_id = c.id
            ORDER BY c.class_name, c.section, s.name
            """)
            students = cursor.fetchall()

            print("\n" + "="*50)
            print("            ALL STUDENTS BY CLASS & SECTION")
            print("="*50)

            if not students:
                print("No students found.")
                return

            current_class_section = None
            class_counts = {}

            for student in students:
                class_section_key = f"{student['class_name']}-{student['section']}"

                # Track counts
                if class_section_key not in class_counts:
                    class_counts[class_section_key] = 0
                class_counts[class_section_key] += 1

                # Print class section header if changed
                if class_section_key != current_class_section:
                    if current_class_section is not None:
                        print()  # Add spacing between groups
                    current_class_section = class_section_key
                    print(f"\n📚 {student['class_name']} - Section {student['section']}")
                    print("-" * 50)

                print(f"Admission No: {student['admission_number']}")
                print(f"Name: {student['name']}")
                print(f"Father: {student['father_name']} ({student['father_occupation']})")
                print(f"Mother: {student['mother_name']} ({student['mother_occupation']})")
                print(f"Contact: {student['contact_number']}")
                print("-" * 30)

            print(f"\n{'='*50}")
            print("CLASS & SECTION SUMMARY:")
            for class_section, count in class_counts.items():
                print(f"{class_section}: {count} students")

            print(f"\nTotal Students: {len(students)}")
            print(f"Total Class-Sections: {len(class_counts)}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()
    
    def view_all_classes(self):
        """View all classes"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
            SELECT c.*, COUNT(s.id) as student_count, COUNT(sub.id) as subject_count
            FROM classes c 
            LEFT JOIN students s ON c.id = s.class_id 
            LEFT JOIN subjects sub ON c.id = sub.class_id 
            GROUP BY c.id 
            ORDER BY c.class_name, c.section
            """)
            classes = cursor.fetchall()
            
            print("\n" + "="*50)
            print("            ALL CLASSES")
            print("="*50)
            
            for cls in classes:
                print(f"\nClass: {cls['class_name']}-{cls['section']}")
                print(f"Students: {cls['student_count']}")
                print(f"Subjects: {cls['subject_count']}")
                print("-" * 30)
            
            print(f"\nTotal Classes: {len(classes)}")
            
        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()
    
    def teacher_dashboard(self):
        """
        Display and handle the teacher dashboard menu.

        Presents a menu-driven interface for teacher operations including student
        attendance management, timetable viewing, profile access, and credential
        updates. Some options may be restricted based on teacher privileges
        configured by administrators. Runs in a continuous loop until logout.

        Menu Options:
            1. Mark Student Attendance - For assigned classes only
            2. View My Timetable - Shows assigned lectures
            3. View My Attendance - Personal attendance history
            4. View My Students - Students in assigned classes
            5. View My Profile - Personal information and privileges
            6. Change Username & Password - Credential management
            7. Manage Student Status - Suspension/unsuspension (privileged)
            8. View My Assigned Classes - Overview of assignments
            9. View Student Attendance History - For assigned students
            10. Edit Student Attendance - Privilege-dependent
            11. Logout

        Note:
            Teacher access is restricted to assigned classes and subjects.
            Privilege checks are performed for sensitive operations.
        """
        while True:
            print("\n" + "="*50)
            print("            TEACHER DASHBOARD")
            print("="*50)
            print("1. Mark Student Attendance")
            print("2. View My Timetable")
            print("3. View My Attendance")
            print("4. View My Students")
            print("5. View My Profile")
            print("6. Change Username & Password")
            print("7. Manage Student Status")
            print("8. View My Assigned Classes")
            print("9. View Student Attendance History")
            print("10. Edit Student Attendance")
            print("11. Logout")

            choice = input("\nEnter your choice (1-11): ").strip()

            if choice == '1':
                self.mark_student_attendance()
            elif choice == '2':
                self.view_teacher_timetable()
            elif choice == '3':
                self.view_teacher_attendance()
            elif choice == '4':
                self.view_teacher_students()
            elif choice == '5':
                self.view_teacher_profile()
            elif choice == '6':
                self.change_teacher_credentials()
            elif choice == '7':
                self.teacher_manage_student_status()
            elif choice == '8':
                self.view_teacher_assigned_classes()
            elif choice == '9':
                self.view_student_attendance_history()
            elif choice == '10':
                self.edit_student_attendance()
            elif choice == '11':
                self.logout()
                break
            else:
                print("Invalid choice! Please try again.")
    
    def mark_student_attendance(self):
        """Mark attendance for students in teacher's assigned classes only"""
        print("\n" + "="*50)
        print("        MARK STUDENT ATTENDANCE")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Get only classes where teacher is explicitly assigned
            cursor.execute("""
            SELECT DISTINCT c.id, c.class_name, c.section
            FROM teacher_assignments ta
            JOIN classes c ON ta.class_id = c.id
            WHERE ta.teacher_id = (SELECT id FROM teachers WHERE user_id = %s)
            ORDER BY c.class_name, c.section
            """, (self.current_user['id'],))

            classes = cursor.fetchall()

            if not classes:
                print("No classes assigned to you.")
                print("Note: You can only mark attendance for classes you are explicitly assigned to by the admin.")
                return

            print("Your Assigned Classes:")
            for cls in classes:
                print(f"{cls['id']}. {cls['class_name']} - Section {cls['section']}")

            class_id = int(input("\nSelect Class ID: "))

            # Verify this class is assigned to the teacher
            cursor.execute("""
            SELECT c.class_name, c.section FROM classes c
            JOIN teacher_assignments ta ON ta.class_id = c.id
            WHERE c.id = %s AND ta.teacher_id = (SELECT id FROM teachers WHERE user_id = %s)
            """, (class_id, self.current_user['id']))

            assigned_class = cursor.fetchone()
            if not assigned_class:
                print("You are not assigned to this class!")
                return

            attendance_date = input("Date (YYYY-MM-DD) [Today]: ").strip()
            if not attendance_date:
                attendance_date = date.today().isoformat()

            # Get only active students from assigned class (ensure proper section segregation)
            cursor.execute("""
            SELECT DISTINCT s.id, s.name, s.admission_number
            FROM students s
            LEFT JOIN student_status ss ON s.id = ss.student_id
            LEFT JOIN student_subjects sts ON s.id = sts.student_id
            LEFT JOIN subjects sub ON sts.subject_id = sub.id
            WHERE s.class_id = %s AND (ss.status IS NULL OR ss.status = 'active')
            AND (sub.class_id IS NULL OR sub.class_id = %s)
            ORDER BY s.name
            """, (class_id, class_id))

            students = cursor.fetchall()

            if not students:
                print("No active students in this assigned class.")
                return

            print(f"\nMarking attendance for {assigned_class['class_name']}-{assigned_class['section']} on {attendance_date}")
            print("Enter 'P' for Present, 'A' for Absent, or press Enter for Absent")
            print("-" * 60)

            for student in students:
                status = input(f"{student['name']} ({student['admission_number']}) [P/A]: ").strip().upper()
                final_status = 'present' if status == 'P' else 'absent'

                # Check if attendance already exists
                cursor.execute(
                    "SELECT id FROM student_attendance WHERE student_id = %s AND date = %s",
                    (student['id'], attendance_date)
                )
                existing = cursor.fetchone()

                if existing:
                    # Update existing
                    update_query = """
                    UPDATE student_attendance
                    SET status = %s, recorded_by = %s, recorded_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                    """
                    cursor.execute(update_query, (final_status, self.current_user['id'], existing['id']))
                else:
                    # Insert new
                    insert_query = """
                    INSERT INTO student_attendance (student_id, date, status, recorded_by)
                    VALUES (%s, %s, %s, %s)
                    """
                    cursor.execute(insert_query, (student['id'], attendance_date, final_status, self.current_user['id']))

            self.connection.commit()
            print(f"\n✓ Attendance marked successfully for {len(students)} students in {assigned_class['class_name']}-{assigned_class['section']}!")

        except ValueError:
            print("Invalid class ID!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def get_teacher_id(self):
        """Get teacher ID for current user"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        try:
            cursor.execute("SELECT id FROM teachers WHERE user_id = %s", (self.current_user['id'],))
            teacher = cursor.fetchone()
            return teacher['id'] if teacher else None
        finally:
            cursor.close()
    
    def view_teacher_timetable(self):
        """View teacher's timetable - only shows lectures assigned to this teacher"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT tt.day_of_week, tt.lecture_number, tt.start_time, tt.end_time,
                   s.subject_name, c.class_name, c.section,
                   tt.break_start_time, tt.break_end_time
            FROM timetable tt
            LEFT JOIN subjects s ON tt.subject_id = s.id
            JOIN classes c ON tt.class_id = c.id
            WHERE tt.teacher_id = (SELECT id FROM teachers WHERE user_id = %s)
            ORDER BY
                FIELD(tt.day_of_week, 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'),
                tt.lecture_number
            """, (self.current_user['id'],))

            timetable = cursor.fetchall()

            print("\n" + "="*70)
            print("                YOUR TIMETABLE")
            print("="*70)
            print("Only showing lectures assigned to you")

            if not timetable:
                print("No timetable entries found for your assigned classes.")
                return

            current_day = None
            total_lectures = 0

            for entry in timetable:
                if entry['day_of_week'] != current_day:
                    if current_day is not None:
                        print()  # Add spacing between days
                    current_day = entry['day_of_week']
                    print(f"\n{current_day.upper()}:")
                    print("-" * 65)

                # Check if this is a break period
                if entry['break_start_time'] and entry['break_end_time']:
                    print(f"{entry['lecture_number']:<8} BREAK TIME")
                    print(f"{entry['break_start_time']} - {entry['break_end_time']}")
                    print("-" * 30)
                else:
                    print(f"{entry['lecture_number']:<8} Lecture {entry['lecture_number']}")
                    print(f"{entry['start_time']:<12} - {entry['end_time']:<12}")
                    print(f"{entry['subject_name']:<20}")
                    print(f"{entry['class_name']}-{entry['section']}")
                    print("-" * 30)
                    total_lectures += 1

            print(f"\n{'='*70}")
            print("SUMMARY:")
            print(f"Total Lectures Assigned: {total_lectures}")
            print(f"Total Periods (including breaks): {len(timetable)}")
            print("Note: You can only view lectures assigned to you by the admin.")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()
    
    def view_teacher_attendance(self):
        """View teacher's own attendance"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
            SELECT date, status, recorded_at 
            FROM teacher_attendance 
            WHERE teacher_id = (SELECT id FROM teachers WHERE user_id = %s)
            ORDER BY date DESC 
            LIMIT 30
            """, (self.current_user['id'],))
            
            attendance = cursor.fetchall()
            
            print("\n" + "="*50)
            print("            YOUR ATTENDANCE (Last 30 records)")
            print("="*50)
            
            if not attendance:
                print("No attendance records found.")
                return
            
            present_count = 0
            absent_count = 0
            
            for record in attendance:
                status_display = "PRESENT" if record['status'] == 'present' else "ABSENT"
                print(f"Date: {record['date']} | Status: {status_display} | Recorded: {record['recorded_at']}")
                
                if record['status'] == 'present':
                    present_count += 1
                else:
                    absent_count += 1
            
            total = len(attendance)
            if total > 0:
                attendance_percentage = (present_count / total) * 100
                print(f"\nSummary: Present: {present_count} | Absent: {absent_count} | Total: {total}")
                print(f"Attendance Percentage: {attendance_percentage:.1f}%")
            
        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()
    
    def view_teacher_students(self):
        """View students in teacher's assigned classes only"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Get students only from classes where teacher is specifically assigned
            cursor.execute("""
            SELECT DISTINCT s.id, s.name, s.admission_number, c.class_name, c.section,
                           CASE WHEN ss.status IS NULL THEN 'active' ELSE ss.status END as status
            FROM students s
            JOIN classes c ON s.class_id = c.id
            JOIN teacher_assignments ta ON ta.class_id = c.id
            LEFT JOIN student_status ss ON s.id = ss.student_id
            WHERE ta.teacher_id = (SELECT id FROM teachers WHERE user_id = %s)
            ORDER BY c.class_name, c.section, s.name
            """, (self.current_user['id'],))

            students = cursor.fetchall()

            print("\n" + "="*50)
            print("            YOUR ASSIGNED CLASS STUDENTS")
            print("="*50)

            if not students:
                print("No students found in your assigned classes.")
                print("Note: You can only view students from classes you are explicitly assigned to by the admin.")
                return

            current_class = None
            total_students = 0
            active_count = 0
            suspended_count = 0

            for student in students:
                class_display = f"{student['class_name']}-{student['section']}"
                if class_display != current_class:
                    if current_class is not None:
                        print()  # Add spacing between classes
                    current_class = class_display
                    print(f"\nClass: {current_class}")
                    print("-" * 40)

                status_display = "ACTIVE" if student['status'] == 'active' else student['status'].upper()
                print(f"  {student['name']} ({student['admission_number']}) - {status_display}")

                total_students += 1
                if student['status'] == 'active':
                    active_count += 1
                elif student['status'] == 'suspended':
                    suspended_count += 1

            print(f"\n{'='*50}")
            print(f"Summary for your assigned classes:")
            print(f"Total Students: {total_students}")
            print(f"Active: {active_count}")
            print(f"Suspended: {suspended_count}")
            print(f"Note: You can only manage students from your assigned classes.")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()
    
    def student_dashboard(self):
        """
        Display and handle the student dashboard menu.

        Presents a menu interface for student-specific functions including personal
        timetable viewing, attendance tracking, subject information, profile access,
        and credential management. Students have read-only access to most data.
        Runs in a continuous loop until logout is selected.

        Menu Options:
            1. View My Timetable - Class schedule
            2. View My Attendance - Current attendance summary
            3. View My Subjects - Enrolled subjects with teachers
            4. View My Profile - Personal information
            5. Change Username & Password - Account credentials
            6. View Attendance History - Detailed attendance records
            7. Logout

        Note:
            All data access is filtered to the logged-in student's records only.
            Credential changes are handled securely with confirmation.
        """
        while True:
            print("\n" + "="*50)
            print("            STUDENT DASHBOARD")
            print("="*50)
            print("1. View My Timetable")
            print("2. View My Attendance")
            print("3. View My Subjects")
            print("4. View My Profile")
            print("5. Change Username & Password")
            print("6. View Attendance History")
            print("7. Logout")

            choice = input("\nEnter your choice (1-7): ").strip()

            if choice == '1':
                self.view_student_timetable()
            elif choice == '2':
                self.view_student_attendance()
            elif choice == '3':
                self.view_student_subjects()
            elif choice == '4':
                self.view_student_profile()
            elif choice == '5':
                self.change_student_credentials()
            elif choice == '6':
                # For students, show their own attendance history
                cursor = self.connection.cursor(pymysql.cursors.DictCursor)
                try:
                    cursor.execute("""
                    SELECT sa.date, sa.status, sa.recorded_at,
                           u.username as recorded_by_name
                    FROM student_attendance sa
                    LEFT JOIN users u ON sa.recorded_by = u.id
                    WHERE sa.student_id = (SELECT id FROM students WHERE user_id = %s)
                    ORDER BY sa.date DESC, sa.recorded_at DESC
                    """, (self.current_user['id'],))

                    attendance_records = cursor.fetchall()

                    print("\n" + "="*50)
                    print("        YOUR ATTENDANCE HISTORY")
                    print("="*50)

                    if not attendance_records:
                        print("No attendance records found.")
                    else:
                        # Calculate statistics
                        total_records = len(attendance_records)
                        present_count = sum(1 for record in attendance_records if record['status'] == 'present')
                        absent_count = total_records - present_count
                        attendance_percentage = (present_count / total_records * 100) if total_records > 0 else 0

                        print(f"Total Records: {total_records} | Present: {present_count} | Absent: {absent_count} | Attendance: {attendance_percentage:.1f}%")
                        print("-" * 100)

                        for record in attendance_records:
                            status_display = "PRESENT" if record['status'] == 'present' else "ABSENT"
                            recorded_by = record['recorded_by_name'] if record['recorded_by_name'] != 'Admin' else 'Admin'

                            print("{:<12} {:<8} {:<20} {}".format(
                                str(record['date']),
                                status_display,
                                str(record['recorded_at']),
                                recorded_by
                            ))

                        print("-" * 100)
                        print(f"Summary: Present: {present_count} | Absent: {absent_count} | Total: {total_records} | Percentage: {attendance_percentage:.1f}%")

                except pymysql.Error as err:
                    print(f"Database error: {err}")
                finally:
                    cursor.close()
            elif choice == '7':
                self.logout()
                break
            else:
                print("Invalid choice! Please try again.")
    
    def view_student_timetable(self):
        """View student's timetable"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
            SELECT tt.day_of_week, tt.lecture_number, tt.start_time, tt.end_time,
                   s.subject_name, t.name as teacher_name
            FROM timetable tt
            JOIN subjects s ON tt.subject_id = s.id
            JOIN teachers t ON tt.teacher_id = t.id
            WHERE tt.class_id = (SELECT class_id FROM students WHERE user_id = %s)
            ORDER BY 
                FIELD(tt.day_of_week, 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'),
                tt.lecture_number
            """, (self.current_user['id'],))
            
            timetable = cursor.fetchall()
            
            print("\n" + "="*50)
            print("            YOUR TIMETABLE")
            print("="*50)
            
            if not timetable:
                print("No timetable entries found.")
                return
            
            current_day = None
            for entry in timetable:
                if entry['day_of_week'] != current_day:
                    current_day = entry['day_of_week']
                    print(f"\n{current_day.upper()}:")
                    print("-" * 50)
                
                print(f"  Lecture {entry['lecture_number']}: {entry['start_time']} - {entry['end_time']}")
                print(f"  Subject: {entry['subject_name']}")
                print(f"  Teacher: {entry['teacher_name']}")
                print()
            
        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()
    
    def view_student_attendance(self):
        """View student's own attendance"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)
        
        try:
            cursor.execute("""
            SELECT date, status, recorded_at 
            FROM student_attendance 
            WHERE student_id = (SELECT id FROM students WHERE user_id = %s)
            ORDER BY date DESC 
            LIMIT 30
            """, (self.current_user['id'],))
            
            attendance = cursor.fetchall()
            
            print("\n" + "="*50)
            print("            YOUR ATTENDANCE (Last 30 records)")
            print("="*50)
            
            if not attendance:
                print("No attendance records found.")
                return
            
            present_count = 0
            absent_count = 0
            
            for record in attendance:
                status_display = "PRESENT" if record['status'] == 'present' else "ABSENT"
                print(f"Date: {record['date']} | Status: {status_display} | Recorded: {record['recorded_at']}")
                
                if record['status'] == 'present':
                    present_count += 1
                else:
                    absent_count += 1
            
            total = len(attendance)
            if total > 0:
                attendance_percentage = (present_count / total) * 100
                print(f"\nSummary: Present: {present_count} | Absent: {absent_count} | Total: {total}")
                print(f"Attendance Percentage: {attendance_percentage:.1f}%")
            
        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()
    
    def view_student_subjects(self):
        """View student's subjects"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT s.subject_name, t.name as teacher_name
            FROM subjects s
            JOIN teachers t ON s.teacher_id = t.id
            WHERE s.class_id = (SELECT class_id FROM students WHERE user_id = %s)
            ORDER BY s.subject_name
            """, (self.current_user['id'],))

            subjects = cursor.fetchall()

            print("\n" + "="*50)
            print("            YOUR SUBJECTS")
            print("="*50)

            if not subjects:
                print("No subjects found.")
                return

            for subject in subjects:
                print(f"Subject: {subject['subject_name']}")
                print(f"Teacher: {subject['teacher_name']}")
                print("-" * 30)

            print(f"\nTotal Subjects: {len(subjects)}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def view_student_attendance_history(self):
        """View full attendance history for a specific student"""
        print("\n" + "="*50)
        print("    STUDENT ATTENDANCE HISTORY")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show all students for selection
            cursor.execute("""
            SELECT s.id, s.name, s.admission_number, c.class_name, c.section
            FROM students s
            JOIN classes c ON s.class_id = c.id
            ORDER BY c.class_name, c.section, s.name
            """)

            students = cursor.fetchall()

            if not students:
                print("No students found.")
                return

            print("\nAvailable Students:")
            print("-" * 80)
            for student in students:
                print("{}. {} ({}) - {}-{}".format(
                    student['id'], student['name'], student['admission_number'],
                    student['class_name'], student['section']))

            student_id = int(input("\nEnter Student ID to view attendance history: "))

            # Verify student exists
            cursor.execute("""
            SELECT s.name, s.admission_number, c.class_name, c.section
            FROM students s
            JOIN classes c ON s.class_id = c.id
            WHERE s.id = %s
            """, (student_id,))

            student = cursor.fetchone()
            if not student:
                print("Student not found!")
                return

            print(f"\nAttendance History for: {student['name']} ({student['admission_number']})")
            print(f"Class: {student['class_name']}-{student['section']}")
            print("-" * 100)

            # Get attendance history with user info
            cursor.execute("""
            SELECT sa.date, sa.status, sa.recorded_at,
                   u.username as recorded_by_name
            FROM student_attendance sa
            LEFT JOIN users u ON sa.recorded_by = u.id
            WHERE sa.student_id = %s
            ORDER BY sa.date DESC, sa.recorded_at DESC
            """, (student_id,))

            attendance_records = cursor.fetchall()

            if not attendance_records:
                print("No attendance records found for this student.")
                return

            # Calculate statistics
            total_records = len(attendance_records)
            present_count = sum(1 for record in attendance_records if record['status'] == 'present')
            absent_count = total_records - present_count
            attendance_percentage = (present_count / total_records * 100) if total_records > 0 else 0

            print(f"Total Records: {total_records} | Present: {present_count} | Absent: {absent_count} | Attendance: {attendance_percentage:.1f}%")
            print("-" * 100)

            for record in attendance_records:
                status_display = "PRESENT" if record['status'] == 'present' else "ABSENT"
                recorded_by = record['recorded_by_name'] if record['recorded_by_name'] != 'Admin' else 'Admin'

                print("{:<12} {:<8} {:<20} {}".format(
                    str(record['date']),
                    status_display,
                    str(record['recorded_at']),
                    recorded_by
                ))

            print("-" * 100)
            print(f"Summary: Present: {present_count} | Absent: {absent_count} | Total: {total_records} | Percentage: {attendance_percentage:.1f}%")

        except ValueError:
            print("Invalid student ID!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def edit_student_attendance(self):
        """Edit student attendance record (Admin or privileged teachers only)"""
        print("\n" + "="*50)
        print("    EDIT STUDENT ATTENDANCE")
        print("="*50)

        # Permission check
        if self.current_role == 'teacher':
            cursor = self.connection.cursor(pymysql.cursors.DictCursor)
            try:
                cursor.execute("SELECT can_edit_attendance FROM teacher_privileges WHERE teacher_id = (SELECT id FROM teachers WHERE user_id = %s)", (self.current_user['id'],))
                priv = cursor.fetchone()
                if not priv or not priv['can_edit_attendance']:
                    print("You don't have permission to edit attendance records.")
                    return
            finally:
                cursor.close()
        elif self.current_role != 'admin':
            print("Access denied. Only admin and privileged teachers can edit attendance.")
            return

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show all students for selection
            cursor.execute("""
            SELECT s.id, s.name, s.admission_number, c.class_name, c.section
            FROM students s
            JOIN classes c ON s.class_id = c.id
            ORDER BY c.class_name, c.section, s.name
            """)

            students = cursor.fetchall()

            if not students:
                print("No students found.")
                return

            print("\nAvailable Students:")
            print("-" * 80)
            for student in students:
                print("{}. {} ({}) - {}-{}".format(
                    student['id'], student['name'], student['admission_number'],
                    student['class_name'], student['section']))

            student_id = int(input("\nEnter Student ID to edit attendance: "))

            # Verify student exists
            cursor.execute("""
            SELECT s.name, s.admission_number, c.class_name, c.section
            FROM students s
            JOIN classes c ON s.class_id = c.id
            WHERE s.id = %s
            """, (student_id,))

            student = cursor.fetchone()
            if not student:
                print("Student not found!")
                return

            print(f"\nEditing attendance for: {student['name']} ({student['admission_number']})")
            print(f"Class: {student['class_name']}-{student['section']}")

            # Get date
            attendance_date = input("Date (YYYY-MM-DD): ").strip()
            if not attendance_date:
                print("Date is required!")
                return

            # Check if attendance record exists
            cursor.execute("""
            SELECT sa.id, sa.status, sa.recorded_at,
                   u.username as recorded_by_name
            FROM student_attendance sa
            LEFT JOIN users u ON sa.recorded_by = u.id
            WHERE sa.student_id = %s AND sa.date = %s
            """, (student_id, attendance_date))

            existing_record = cursor.fetchone()

            if existing_record:
                print(f"\nCurrent Record:")
                print(f"Date: {attendance_date}")
                print(f"Status: {existing_record['status'].upper()}")
                print(f"Recorded: {existing_record['recorded_at']}")
                print(f"By: {existing_record['recorded_by_name']}")

                # Ask for new status
                new_status = input("New Status (present/absent): ").strip().lower()
                if new_status not in ['present', 'absent']:
                    print("Invalid status. Must be 'present' or 'absent'.")
                    return

                # Update record
                cursor.execute("""
                UPDATE student_attendance
                SET status = %s, recorded_by = %s, recorded_at = CURRENT_TIMESTAMP
                WHERE id = %s
                """, (new_status, self.current_user['id'], existing_record['id']))

                print(f"✓ Attendance updated successfully! Changed to {new_status.upper()}")

            else:
                # Create new record
                new_status = input("Status (present/absent): ").strip().lower()
                if new_status not in ['present', 'absent']:
                    print("Invalid status. Must be 'present' or 'absent'.")
                    return

                cursor.execute("""
                INSERT INTO student_attendance (student_id, date, status, recorded_by)
                VALUES (%s, %s, %s, %s)
                """, (student_id, attendance_date, new_status, self.current_user['id']))

                print(f"✓ New attendance record created! Status: {new_status.upper()}")

            self.connection.commit()

        except ValueError:
            print("Invalid input!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def manage_teacher_privileges(self):
        """Admin: Manage teacher privileges"""
        print("\n" + "="*50)
        print("        MANAGE TEACHER PRIVILEGES")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show all teachers
            cursor.execute("SELECT t.id, t.name, tp.* FROM teachers t LEFT JOIN teacher_privileges tp ON t.id = tp.teacher_id ORDER BY t.name")
            teachers = cursor.fetchall()

            if not teachers:
                print("No teachers found.")
                return

            print("\nTeachers and their privileges:")
            print("-" * 100)
            for teacher in teachers:
                print(f"ID: {teacher['id']} | Name: {teacher['name']}")
                print(f"  Edit Students: {'Yes' if teacher.get('can_edit_students') else 'No'}")
                print(f"  Delete Students: {'Yes' if teacher.get('can_delete_students') else 'No'}")
                print(f"  Suspend Students: {'Yes' if teacher.get('can_suspend_students') else 'No'}")
                print(f"  Edit Subjects: {'Yes' if teacher.get('can_edit_subjects') else 'No'}")
                print(f"  Delete Subjects: {'Yes' if teacher.get('can_delete_subjects') else 'No'}")
                print(f"  Edit Attendance: {'Yes' if teacher.get('can_edit_attendance') else 'No'}")
                print("-" * 50)

            teacher_id = int(input("\nEnter Teacher ID to manage privileges: "))

            # Check if teacher exists
            cursor.execute("SELECT name FROM teachers WHERE id = %s", (teacher_id,))
            teacher = cursor.fetchone()
            if not teacher:
                print("Teacher not found!")
                return

            print(f"\nManaging privileges for: {teacher['name']}")

            # Get current privileges or create if not exist
            cursor.execute("SELECT * FROM teacher_privileges WHERE teacher_id = %s", (teacher_id,))
            priv = cursor.fetchone()

            can_edit_students = input(f"Can edit students? (y/n) [{priv['can_edit_students'] if priv else 'n'}]: ").strip().lower() == 'y'
            can_delete_students = input(f"Can delete students? (y/n) [{priv['can_delete_students'] if priv else 'n'}]: ").strip().lower() == 'y'
            can_suspend_students = input(f"Can suspend students? (y/n) [{priv['can_suspend_students'] if priv else 'n'}]: ").strip().lower() == 'y'
            can_edit_subjects = input(f"Can edit subjects? (y/n) [{priv['can_edit_subjects'] if priv else 'n'}]: ").strip().lower() == 'y'
            can_delete_subjects = input(f"Can delete subjects? (y/n) [{priv['can_delete_subjects'] if priv else 'n'}]: ").strip().lower() == 'y'
            can_edit_attendance = input(f"Can edit attendance? (y/n) [{priv['can_edit_attendance'] if priv else 'n'}]: ").strip().lower() == 'y'

            if priv:
                # Update existing privileges
                update_query = """
                UPDATE teacher_privileges SET
                can_edit_students = %s, can_delete_students = %s, can_suspend_students = %s,
                can_edit_subjects = %s, can_delete_subjects = %s, can_edit_attendance = %s
                WHERE teacher_id = %s
                """
                cursor.execute(update_query, (can_edit_students, can_delete_students, can_suspend_students,
                                            can_edit_subjects, can_delete_subjects, can_edit_attendance, teacher_id))
            else:
                # Insert new privileges
                insert_query = """
                INSERT INTO teacher_privileges (teacher_id, can_edit_students, can_delete_students, can_suspend_students,
                                               can_edit_subjects, can_delete_subjects, can_edit_attendance)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(insert_query, (teacher_id, can_edit_students, can_delete_students, can_suspend_students,
                                            can_edit_subjects, can_delete_subjects, can_edit_attendance))

            self.connection.commit()
            print("Teacher privileges updated successfully!")

        except ValueError:
            print("Invalid teacher ID!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def allot_subjects_to_student(self):
        """Admin: Allot subjects to a student by subject IDs (multiple selection)"""
        print("\n" + "="*50)
        print("    ALLOT SUBJECTS TO STUDENT")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show all students
            cursor.execute("""
            SELECT s.id, s.name, s.admission_number, c.class_name, c.section
            FROM students s
            JOIN classes c ON s.class_id = c.id
            ORDER BY c.class_name, c.section, s.name
            """)

            students = cursor.fetchall()

            if not students:
                print("No students found.")
                return

            print("\nAvailable Students:")
            print("-" * 80)
            for student in students:
                print("{}. {} ({}) - {}-{}".format(
                    student['id'], student['name'], student['admission_number'],
                    student['class_name'], student['section']))

            student_id = int(input("\nEnter Student ID: "))

            # Verify student exists
            cursor.execute("""
            SELECT s.name, s.admission_number, c.class_name, c.section
            FROM students s
            JOIN classes c ON s.class_id = c.id
            WHERE s.id = %s
            """, (student_id,))
            student = cursor.fetchone()

            if not student:
                print("Student not found!")
                return

            print(f"\nAlloting subjects to: {student['name']} ({student['admission_number']})")
            print(f"Class: {student['class_name']}-{student['section']}")

            # Show student's current subjects
            cursor.execute("""
            SELECT ss.id, s.subject_name, s.id as subject_id
            FROM student_subjects ss
            JOIN subjects s ON ss.subject_id = s.id
            WHERE ss.student_id = %s
            ORDER BY s.subject_name
            """, (student_id,))

            current_subjects = cursor.fetchall()

            if current_subjects:
                print(f"\nCurrent subjects ({len(current_subjects)}):")
                for subj in current_subjects:
                    print("  - {} (ID: {})".format(subj['subject_name'], subj['subject_id']))
            else:
                print("\nNo current subjects assigned.")

            # Show all available subjects for the student's class
            cursor.execute("""
            SELECT s.id, s.subject_name, t.name as teacher_name
            FROM subjects s
            LEFT JOIN teachers t ON s.teacher_id = t.id
            WHERE s.class_id = (SELECT class_id FROM students WHERE id = %s)
            ORDER BY s.subject_name
            """, (student_id,))

            available_subjects = cursor.fetchall()

            if not available_subjects:
                print("No subjects available for this student's class.")
                return

            print(f"\nAvailable subjects for {student['class_name']}-{student['section']}:")
            print("-" * 50)
            for subj in available_subjects:
                teacher_name = subj['teacher_name'] if subj['teacher_name'] else "Not assigned"
                print("{}. {} (Teacher: {})".format(subj['id'], subj['subject_name'], teacher_name))

            # Get subject IDs to allot
            subject_ids_input = input("\nEnter Subject IDs to allot (comma-separated, e.g., 1,3,5 or 'all' for all): ").strip()

            if subject_ids_input.lower() == 'all':
                subject_ids = [str(s['id']) for s in available_subjects]
            else:
                subject_ids = [x.strip() for x in subject_ids_input.split(',') if x.strip()]

            if not subject_ids:
                print("No subject IDs provided.")
                return

            # Validate subject IDs
            validated_subject_ids = []
            for subj_id in subject_ids:
                try:
                    subj_id_int = int(subj_id)
                    # Check if subject exists and belongs to student's class
                    cursor.execute("""
                    SELECT s.subject_name FROM subjects s
                    WHERE s.id = %s AND s.class_id = (SELECT class_id FROM students WHERE id = %s)
                    """, (subj_id_int, student_id))
                    subj_info = cursor.fetchone()
                    if subj_info:
                        validated_subject_ids.append((subj_id_int, subj_info['subject_name']))
                    else:
                        print("Subject ID {} not found for this student's class.".format(subj_id))
                except ValueError:
                    print("Invalid subject ID: {}".format(subj_id))

            if not validated_subject_ids:
                print("No valid subject IDs provided.")
                return

            # Confirm allotment
            print(f"\nAlloting the following subjects to {student['name']}:")
            for subj_id, subj_name in validated_subject_ids:
                print("  - {}".format(subj_name))

            confirm = input("\nProceed with allotment? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Allotment cancelled.")
                return

            # Clear existing subject assignments for this student
            cursor.execute("DELETE FROM student_subjects WHERE student_id = %s", (student_id,))

            # Add new subject assignments
            allotted_count = 0
            for subj_id, subj_name in validated_subject_ids:
                try:
                    cursor.execute("""
                    INSERT INTO student_subjects (student_id, subject_id)
                    VALUES (%s, %s)
                    """, (student_id, subj_id))
                    allotted_count += 1
                    print("✓ Allotted: {}".format(subj_name))
                except pymysql.IntegrityError:
                    print("⚠️  Subject {} already allotted".format(subj_name))

            self.connection.commit()

            print(f"\n🎉 Subject allotment completed successfully!")
            print(f"Student: {student['name']} ({student['admission_number']})")
            print(f"Total subjects allotted: {allotted_count}")
            print(f"Previous subjects removed and replaced with selected combination.")

        except ValueError:
            print("Invalid input! Please enter numbers for IDs.")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def allot_subjects_to_class(self):
        """Admin: Allot subjects to a class by selecting from subject lists using IDs"""
        print("\n" + "="*50)
        print("    ALLOT SUBJECTS TO CLASS")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show available classes
            cursor.execute("SELECT * FROM classes ORDER BY class_name, section")
            classes = cursor.fetchall()

            if not classes:
                print("No classes available.")
                return

            print("\nAvailable Classes:")
            for cls in classes:
                print("{}. {}-{}".format(cls['id'], cls['class_name'], cls['section']))

            class_id = int(input("\nEnter Class ID: "))

            # Verify class exists
            cursor.execute("SELECT class_name, section FROM classes WHERE id = %s", (class_id,))
            class_info = cursor.fetchone()

            if not class_info:
                print("Class not found!")
                return

            print(f"\nAlloting subjects to: {class_info['class_name']}-{class_info['section']}")

            # Show current subjects for this class
            cursor.execute("""
            SELECT s.id, s.subject_name, t.name as teacher_name
            FROM subjects s
            LEFT JOIN teachers t ON s.teacher_id = t.id
            WHERE s.class_id = %s
            ORDER BY s.subject_name
            """, (class_id,))

            current_subjects = cursor.fetchall()

            if current_subjects:
                print(f"\nCurrent subjects in {class_info['class_name']}-{class_info['section']}:")
                for subj in current_subjects:
                    teacher_name = subj['teacher_name'] if subj['teacher_name'] else "Not assigned"
                    print("  - {} (ID: {}, Teacher: {})".format(subj['subject_name'], subj['id'], teacher_name))
            else:
                print(f"\nNo subjects currently assigned to {class_info['class_name']}-{class_info['section']}.")

            # Show all available subjects that could be added to this class
            # Include both existing subjects from other classes and allow creating new ones
            cursor.execute("""
            SELECT s.id, s.subject_name, s.class_id, c.class_name, c.section, t.name as teacher_name
            FROM subjects s
            JOIN classes c ON s.class_id = c.id
            LEFT JOIN teachers t ON s.teacher_id = t.id
            ORDER BY s.subject_name, c.class_name, c.section
            """)

            all_subjects = cursor.fetchall()

            if not all_subjects:
                print("No subjects available in the system.")
                print("Please create subjects first.")
                return

            print(f"\nAll available subjects in the system:")
            print("-" * 60)
            for subj in all_subjects:
                teacher_name = subj['teacher_name'] if subj['teacher_name'] else "Not assigned"
                current_class = "{}-{}".format(subj['class_name'], subj['section'])
                status = " [CURRENT CLASS]" if subj['class_id'] == class_id else ""
                print("{}. {} (Teacher: {}, Current Class: {}){}".format(
                    subj['id'], subj['subject_name'], teacher_name, current_class, status))

            # Get subject IDs to allot to this class
            subject_ids_input = input(f"\nEnter Subject IDs to allot to {class_info['class_name']}-{class_info['section']} (comma-separated): ").strip()

            if not subject_ids_input:
                print("No subject IDs provided.")
                return

            subject_ids = [x.strip() for x in subject_ids_input.split(',') if x.strip()]

            if not subject_ids:
                print("No valid subject IDs provided.")
                return

            # Validate subject IDs exist
            validated_subjects = []
            for subj_id in subject_ids:
                try:
                    subj_id_int = int(subj_id)
                    # Find the subject details
                    subj_info = next((s for s in all_subjects if s['id'] == subj_id_int), None)
                    if subj_info:
                        validated_subjects.append(subj_info)
                    else:
                        print("Subject ID {} not found.".format(subj_id))
                except ValueError:
                    print("Invalid subject ID: {}".format(subj_id))

            if not validated_subjects:
                print("No valid subject IDs provided.")
                return

            # Confirm allotment
            print(f"\nAlloting the following subjects to {class_info['class_name']}-{class_info['section']}:")
            for subj in validated_subjects:
                teacher_name = subj['teacher_name'] if subj['teacher_name'] else "Not assigned"
                print("  - {} (Current Teacher: {})".format(subj['subject_name'], teacher_name))

            confirm = input("\nProceed with allotment? This will update subject-class associations. (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Allotment cancelled.")
                return

            # Process subject allotments
            allotted_count = 0
            updated_count = 0

            for subj in validated_subjects:
                subj_id = subj['id']
                subj_name = subj['subject_name']

                # Check if subject is already in this class
                cursor.execute("SELECT id FROM subjects WHERE id = %s AND class_id = %s", (subj_id, class_id))
                existing = cursor.fetchone()

                if existing:
                    print("⚠️  Subject '{}' is already in this class".format(subj_name))
                else:
                    # Update subject's class_id
                    cursor.execute("UPDATE subjects SET class_id = %s WHERE id = %s", (class_id, subj_id))
                    allotted_count += 1
                    print("✓ Allotted '{}' to {}-{}".format(subj_name, class_info['class_name'], class_info['section']))

                    # Check if there are students in this class who should get this subject
                    cursor.execute("SELECT id, name FROM students WHERE class_id = %s", (class_id,))
                    class_students = cursor.fetchall()

                    if class_students:
                        for student in class_students:
                            # Check if student already has this subject
                            cursor.execute("""
                            SELECT id FROM student_subjects
                            WHERE student_id = %s AND subject_id = %s
                            """, (student['id'], subj_id))

                            if not cursor.fetchone():
                                # Add subject to student's subjects
                                cursor.execute("""
                                INSERT INTO student_subjects (student_id, subject_id)
                                VALUES (%s, %s)
                                """, (student['id'], subj_id))
                                print("  ✓ Added '{}' to student: {}".format(subj_name, student['name']))

            self.connection.commit()

            print(f"\n🎉 Subject allotment to class completed successfully!")
            print(f"Class: {class_info['class_name']}-{class_info['section']}")
            print(f"Total subjects allotted: {allotted_count}")
            print(f"Students automatically updated with new subjects.")

        except ValueError:
            print("Invalid input! Please enter numbers for IDs.")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def reassign_subject_teacher(self):
        """Admin: Reassign subject teacher"""
        print("\n" + "="*50)
        print("    REASSIGN SUBJECT TEACHER")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show all subjects with current teachers
            cursor.execute("""
            SELECT s.id, s.subject_name, c.class_name, c.section,
                   t.name as current_teacher, s.teacher_id
            FROM subjects s
            JOIN classes c ON s.class_id = c.id
            LEFT JOIN teachers t ON s.teacher_id = t.id
            ORDER BY c.class_name, c.section, s.subject_name
            """)

            subjects = cursor.fetchall()

            if not subjects:
                print("No subjects found.")
                return

            print("\nAvailable Subjects:")
            print("-" * 80)
            for subj in subjects:
                teacher_name = subj['current_teacher'] if subj['current_teacher'] else "Not assigned"
                print("{}. {} ({}-{}) - Current Teacher: {}".format(
                    subj['id'], subj['subject_name'], subj['class_name'],
                    subj['section'], teacher_name))

            subject_id = int(input("\nEnter Subject ID to reassign: "))

            # Verify subject exists
            cursor.execute("""
            SELECT s.subject_name, c.class_name, c.section, s.teacher_id
            FROM subjects s
            JOIN classes c ON s.class_id = c.id
            WHERE s.id = %s
            """, (subject_id,))
            subject = cursor.fetchone()

            if not subject:
                print("Subject not found!")
                return

            print(f"\nReassigning: {subject['subject_name']} ({subject['class_name']}-{subject['section']})")

            # Show available teachers
            cursor.execute("SELECT id, name, teaching_subject FROM teachers ORDER BY name")
            teachers = cursor.fetchall()

            if not teachers:
                print("No teachers available.")
                return

            print(f"\nAvailable Teachers:")
            print("-" * 40)
            for teacher in teachers:
                print("{}. {} - {}".format(teacher['id'], teacher['name'], teacher['teaching_subject']))

            teacher_id = int(input(f"\nEnter new Teacher ID for {subject['subject_name']}: "))

            # Verify teacher exists
            cursor.execute("SELECT name FROM teachers WHERE id = %s", (teacher_id,))
            teacher = cursor.fetchone()

            if not teacher:
                print("Teacher not found!")
                return

            # Check if this is the same teacher
            if subject['teacher_id'] == teacher_id:
                print("Subject is already assigned to this teacher!")
                return

            # Update subject teacher
            cursor.execute("UPDATE subjects SET teacher_id = %s WHERE id = %s", (teacher_id, subject_id))

            # Update teacher_assignments table
            # First check if assignment exists
            cursor.execute("""
            SELECT id FROM teacher_assignments
            WHERE teacher_id = %s AND subject_id = %s
            """, (teacher_id, subject_id))

            existing_assignment = cursor.fetchone()

            if not existing_assignment:
                # Remove old assignment if exists
                cursor.execute("DELETE FROM teacher_assignments WHERE subject_id = %s", (subject_id,))
                # Add new assignment
                cursor.execute("""
                INSERT INTO teacher_assignments (teacher_id, class_id, subject_id, assigned_by)
                SELECT %s, class_id, %s, %s FROM subjects WHERE id = %s
                """, (teacher_id, subject_id, self.current_user['id'], subject_id))

            self.connection.commit()

            print(f"✓ Subject '{subject['subject_name']}' reassigned successfully!")
            print(f"New Teacher: {teacher['name']}")

        except ValueError:
            print("Invalid input! Please enter numbers for IDs.")
        except pymysql.Error as err:
            print("Database error: {}".format(err))
            self.connection.rollback()
        finally:
            cursor.close()

    def assign_teachers_to_classes(self):
        """Admin: Assign teachers to specific class-section combinations with subjects"""
        print("\n" + "="*50)
        print("      ASSIGN TEACHERS TO CLASSES & SECTIONS")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show available teachers first
            cursor.execute("SELECT * FROM teachers ORDER BY name")
            teachers = cursor.fetchall()

            if not teachers:
                print("No teachers available. Create teachers first.")
                return

            print("\nAvailable Teachers:")
            for teacher in teachers:
                print("{}. {} - {}".format(teacher['id'], teacher['name'], teacher['teaching_subject']))

            teacher_id = int(input("\nSelect Teacher ID to assign: "))

            # Verify teacher exists
            cursor.execute("SELECT name FROM teachers WHERE id = %s", (teacher_id,))
            teacher = cursor.fetchone()
            if not teacher:
                print("Teacher not found!")
                return

            print(f"\nAssigning classes, sections and subjects to: {teacher['name']}")

            # Show available class names
            cursor.execute("SELECT DISTINCT class_name FROM classes ORDER BY class_name")
            class_names = cursor.fetchall()

            if not class_names:
                print("No classes available. Create classes first.")
                return

            print("\nAvailable Class Names:")
            for i, cls in enumerate(class_names, 1):
                print(f"{i}. {cls['class_name']}")

            class_choice = int(input("\nSelect Class Name (number): "))

            if class_choice < 1 or class_choice > len(class_names):
                print("Invalid class selection!")
                return

            selected_class_name = class_names[class_choice - 1]['class_name']

            # Show available sections for selected class
            cursor.execute("SELECT id, section FROM classes WHERE class_name = %s ORDER BY section", (selected_class_name,))
            available_sections = cursor.fetchall()

            if not available_sections:
                print(f"No sections found for {selected_class_name}.")
                return

            print(f"\nAvailable Sections for {selected_class_name}:")
            for section in available_sections:
                print(f"{section['id']}. Section {section['section']}")

            section_ids_input = input(f"\nEnter Section IDs for {selected_class_name} (comma-separated, e.g., 1,2): ").strip()
            if not section_ids_input:
                print("Section IDs are required!")
                return

            try:
                section_ids = [int(x.strip()) for x in section_ids_input.split(',')]
            except ValueError:
                print("Invalid section IDs format!")
                return

            # Validate section IDs belong to selected class
            for section_id in section_ids:
                cursor.execute("SELECT id FROM classes WHERE id = %s AND class_name = %s", (section_id, selected_class_name))
                if not cursor.fetchone():
                    print(f"Section ID {section_id} not found in {selected_class_name}!")
                    return

            print("\nAssignments Summary:")
            print("-" * 60)
            total_assignments = 0

            # Process each selected section
            for section_id in section_ids:
                # Get section info
                cursor.execute("SELECT section FROM classes WHERE id = %s", (section_id,))
                section_name = cursor.fetchone()['section']

                print(f"\n📚 {selected_class_name} - Section {section_name}")

                # Show subjects available for this specific class-section
                cursor.execute("SELECT id, subject_name FROM subjects WHERE class_id = %s ORDER BY subject_name", (section_id,))
                subjects = cursor.fetchall()

                if not subjects:
                    print(f"No subjects found for {selected_class_name}-{section_name}. Skipping...")
                    continue

                print("Available Subjects:")
                for subject in subjects:
                    print(f"  {subject['id']}. {subject['subject_name']}")

                # Get subject IDs to assign
                subject_ids_input = input(f"Enter Subject IDs for {selected_class_name}-{section_name} (comma-separated or 'all'): ").strip()

                if subject_ids_input.lower() == 'all':
                    subject_ids = [s['id'] for s in subjects]
                else:
                    try:
                        subject_ids = [int(x.strip()) for x in subject_ids_input.split(',')]
                    except ValueError:
                        print("Invalid subject IDs format!")
                        return

                # Create assignments for each subject
                for subject_id in subject_ids:
                    # Verify subject belongs to this class-section
                    cursor.execute("SELECT subject_name FROM subjects WHERE id = %s AND class_id = %s",
                                 (subject_id, section_id))
                    subject = cursor.fetchone()
                    if not subject:
                        print(f"Subject ID {subject_id} not found in {selected_class_name}-{section_name}!")
                        continue

                    # Check if assignment already exists
                    cursor.execute("""
                        SELECT id FROM teacher_assignments
                        WHERE teacher_id = %s AND class_id = %s AND subject_id = %s
                    """, (teacher_id, section_id, subject_id))
                    existing = cursor.fetchone()

                    if existing:
                        print(f"⚠️  Assignment already exists: {subject['subject_name']} for {selected_class_name}-{section_name}")
                    else:
                        # Create assignment
                        cursor.execute("""
                            INSERT INTO teacher_assignments (teacher_id, class_id, subject_id, assigned_by)
                            VALUES (%s, %s, %s, %s)
                        """, (teacher_id, section_id, subject_id, self.current_user['id']))

                        # Update subjects table
                        cursor.execute("UPDATE subjects SET teacher_id = %s WHERE id = %s",
                                     (teacher_id, subject_id))

                        print(f"✓ Assigned {subject['subject_name']} to {teacher['name']} for {selected_class_name}-{section_name}")
                        total_assignments += 1

            self.connection.commit()
            print(f"\n🎉 Teacher assignment completed successfully!")
            print(f"Total assignments created: {total_assignments}")
            print(f"Assigned to {len(section_ids)} sections with {total_assignments} subject assignments.")

        except ValueError:
            print("Invalid input! Please enter numbers for IDs.")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def manage_student_status(self):
        """Admin: Manage student status (suspend, unsuspend, remove)"""
        print("\n" + "="*50)
        print("        MANAGE STUDENT STATUS")
        print("="*50)
        print("1. Suspend Student")
        print("2. Unsuspend Student")
        print("3. Remove Student")
        print("4. View Suspended Students")
        print("5. View Removed Students")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == '1':
            self.suspend_student()
        elif choice == '2':
            self.unsuspend_student()
        elif choice == '3':
            self.remove_student()
        elif choice == '4':
            self.view_suspended_students()
        elif choice == '5':
            self.view_removed_students()
        else:
            print("Invalid choice!")

    def suspend_student(self):
        """Suspend a student"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show active students
            cursor.execute("""
            SELECT s.id, s.name, s.admission_number, c.class_name, c.section
            FROM students s
            JOIN classes c ON s.class_id = c.id
            LEFT JOIN student_status ss ON s.id = ss.student_id
            WHERE ss.status IS NULL OR ss.status = 'active'
            ORDER BY c.class_name, c.section, s.name
            """)
            students = cursor.fetchall()

            if not students:
                print("No active students found.")
                return

            print("\nActive Students:")
            for student in students:
                print(f"{student['id']}. {student['name']} ({student['admission_number']}) - {student['class_name']}-{student['section']}")

            student_id = int(input("\nEnter Student ID to suspend: "))
            reason = input("Suspension reason: ").strip()

            if not reason:
                reason = "Administrative suspension"

            # Check if student exists and is active
            cursor.execute("""
            SELECT s.name FROM students s
            LEFT JOIN student_status ss ON s.id = ss.student_id
            WHERE s.id = %s AND (ss.status IS NULL OR ss.status = 'active')
            """, (student_id,))
            student = cursor.fetchone()

            if not student:
                print("Student not found or already suspended/removed!")
                return

            # Insert suspension record
            cursor.execute("""
            INSERT INTO student_status (student_id, status, suspension_reason, suspended_by)
            VALUES (%s, 'suspended', %s, %s)
            ON DUPLICATE KEY UPDATE
            status = 'suspended', suspension_reason = %s, suspended_by = %s, suspended_at = CURRENT_TIMESTAMP
            """, (student_id, reason, self.current_user['id'], reason, self.current_user['id']))

            self.connection.commit()
            print(f"Student {student['name']} suspended successfully!")

        except ValueError:
            print("Invalid student ID!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def unsuspend_student(self):
        """Unsuspend a student"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show suspended students
            cursor.execute("""
            SELECT s.id, s.name, s.admission_number, c.class_name, c.section, ss.suspension_reason
            FROM students s
            JOIN classes c ON s.class_id = c.id
            JOIN student_status ss ON s.id = ss.student_id
            WHERE ss.status = 'suspended'
            ORDER BY c.class_name, c.section, s.name
            """)
            students = cursor.fetchall()

            if not students:
                print("No suspended students found.")
                return

            print("\nSuspended Students:")
            for student in students:
                print(f"{student['id']}. {student['name']} ({student['admission_number']}) - {student['class_name']}-{student['section']}")
                print(f"   Reason: {student['suspension_reason']}")

            student_id = int(input("\nEnter Student ID to unsuspend: "))

            # Check if student is suspended
            cursor.execute("SELECT name FROM students s JOIN student_status ss ON s.id = ss.student_id WHERE s.id = %s AND ss.status = 'suspended'", (student_id,))
            student = cursor.fetchone()

            if not student:
                print("Student not found or not suspended!")
                return

            # Update status to active
            cursor.execute("UPDATE student_status SET status = 'active', suspension_reason = NULL WHERE student_id = %s", (student_id,))

            self.connection.commit()
            print(f"Student {student['name']} unsuspended successfully!")

        except ValueError:
            print("Invalid student ID!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def remove_student(self):
        """Remove a student permanently"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show students who can be removed (not already removed)
            cursor.execute("""
            SELECT s.id, s.name, s.admission_number, c.class_name, c.section
            FROM students s
            JOIN classes c ON s.class_id = c.id
            LEFT JOIN student_status ss ON s.id = ss.student_id
            WHERE ss.status IS NULL OR ss.status != 'removed'
            ORDER BY c.class_name, c.section, s.name
            """)
            students = cursor.fetchall()

            if not students:
                print("No students available for removal.")
                return

            print("\nStudents available for removal:")
            for student in students:
                print(f"{student['id']}. {student['name']} ({student['admission_number']}) - {student['class_name']}-{student['section']}")

            student_id = int(input("\nEnter Student ID to remove: "))

            # Check if student exists and is not removed
            cursor.execute("""
            SELECT s.name FROM students s
            LEFT JOIN student_status ss ON s.id = ss.student_id
            WHERE s.id = %s AND (ss.status IS NULL OR ss.status != 'removed')
            """, (student_id,))
            student = cursor.fetchone()

            if not student:
                print("Student not found or already removed!")
                return

            confirm = input(f"Are you sure you want to remove student {student['name']}? This action cannot be undone! (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Removal cancelled.")
                return

            # Insert removal record
            cursor.execute("""
            INSERT INTO student_status (student_id, status, suspension_reason, suspended_by)
            VALUES (%s, 'removed', 'Administrative removal', %s)
            ON DUPLICATE KEY UPDATE
            status = 'removed', suspension_reason = 'Administrative removal', suspended_by = %s, suspended_at = CURRENT_TIMESTAMP
            """, (student_id, self.current_user['id'], self.current_user['id']))

            self.connection.commit()
            print(f"Student {student['name']} removed successfully!")

        except ValueError:
            print("Invalid student ID!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def view_suspended_students(self):
        """View suspended students"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT s.name, s.admission_number, c.class_name, c.section,
                   ss.suspension_reason, ss.suspended_at, u.username as suspended_by
            FROM students s
            JOIN classes c ON s.class_id = c.id
            JOIN student_status ss ON s.id = ss.student_id
            LEFT JOIN users u ON ss.suspended_by = u.id
            WHERE ss.status = 'suspended'
            ORDER BY ss.suspended_at DESC
            """)
            students = cursor.fetchall()

            print("\n" + "="*50)
            print("        SUSPENDED STUDENTS")
            print("="*50)

            if not students:
                print("No suspended students found.")
                return

            for student in students:
                print(f"\nName: {student['name']}")
                print(f"Admission No: {student['admission_number']}")
                print(f"Class: {student['class_name']}-{student['section']}")
                print(f"Suspended: {student['suspended_at']}")
                print(f"Reason: {student['suspension_reason']}")
                print(f"Suspended by: {student['suspended_by'] or 'Unknown'}")
                print("-" * 40)

            print(f"\nTotal suspended students: {len(students)}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def view_removed_students(self):
        """View removed students"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT s.name, s.admission_number, c.class_name, c.section,
                   ss.suspended_at, u.username as removed_by
            FROM students s
            JOIN classes c ON s.class_id = c.id
            JOIN student_status ss ON s.id = ss.student_id
            LEFT JOIN users u ON ss.suspended_by = u.id
            WHERE ss.status = 'removed'
            ORDER BY ss.suspended_at DESC
            """)
            students = cursor.fetchall()

            print("\n" + "="*50)
            print("        REMOVED STUDENTS")
            print("="*50)

            if not students:
                print("No removed students found.")
                return

            for student in students:
                print(f"\nName: {student['name']}")
                print(f"Admission No: {student['admission_number']}")
                print(f"Class: {student['class_name']}-{student['section']}")
                print(f"Removed: {student['suspended_at']}")
                print(f"Removed by: {student['removed_by'] or 'Unknown'}")
                print("-" * 40)

            print(f"\nTotal removed students: {len(students)}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def manage_teacher_status(self):
        """Admin: Manage teacher status (suspend, unsuspend, remove)"""
        print("\n" + "="*50)
        print("        MANAGE TEACHER STATUS")
        print("="*50)
        print("1. Suspend Teacher")
        print("2. Unsuspend Teacher")
        print("3. Remove Teacher")
        print("4. View Suspended Teachers")
        print("5. View Removed Teachers")

        choice = input("\nEnter choice (1-5): ").strip()

        if choice == '1':
            self.suspend_teacher()
        elif choice == '2':
            self.unsuspend_teacher()
        elif choice == '3':
            self.remove_teacher()
        elif choice == '4':
            self.view_suspended_teachers()
        elif choice == '5':
            self.view_removed_teachers()
        else:
            print("Invalid choice!")

    def suspend_teacher(self):
        """Suspend a teacher"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show active teachers
            cursor.execute("""
            SELECT t.id, t.name, t.teaching_subject
            FROM teachers t
            LEFT JOIN teacher_status ts ON t.id = ts.teacher_id
            WHERE ts.status IS NULL OR ts.status = 'active'
            ORDER BY t.name
            """)
            teachers = cursor.fetchall()

            if not teachers:
                print("No active teachers found.")
                return

            print("\nActive Teachers:")
            for teacher in teachers:
                print(f"{teacher['id']}. {teacher['name']} - {teacher['teaching_subject']}")

            teacher_id = int(input("\nEnter Teacher ID to suspend: "))
            reason = input("Suspension reason: ").strip()

            if not reason:
                reason = "Administrative suspension"

            # Check if teacher exists and is active
            cursor.execute("""
            SELECT t.name FROM teachers t
            LEFT JOIN teacher_status ts ON t.id = ts.teacher_id
            WHERE t.id = %s AND (ts.status IS NULL OR ts.status = 'active')
            """, (teacher_id,))
            teacher = cursor.fetchone()

            if not teacher:
                print("Teacher not found or already suspended/removed!")
                return

            # Insert suspension record
            cursor.execute("""
            INSERT INTO teacher_status (teacher_id, status, suspension_reason, suspended_by)
            VALUES (%s, 'suspended', %s, %s)
            ON DUPLICATE KEY UPDATE
            status = 'suspended', suspension_reason = %s, suspended_by = %s, suspended_at = CURRENT_TIMESTAMP
            """, (teacher_id, reason, self.current_user['id'], reason, self.current_user['id']))

            self.connection.commit()
            print(f"Teacher {teacher['name']} suspended successfully!")

        except ValueError:
            print("Invalid teacher ID!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def unsuspend_teacher(self):
        """Unsuspend a teacher"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show suspended teachers
            cursor.execute("""
            SELECT t.id, t.name, t.teaching_subject, ts.suspension_reason
            FROM teachers t
            JOIN teacher_status ts ON t.id = ts.teacher_id
            WHERE ts.status = 'suspended'
            ORDER BY t.name
            """)
            teachers = cursor.fetchall()

            if not teachers:
                print("No suspended teachers found.")
                return

            print("\nSuspended Teachers:")
            for teacher in teachers:
                print(f"{teacher['id']}. {teacher['name']} - {teacher['teaching_subject']}")
                print(f"   Reason: {teacher['suspension_reason']}")

            teacher_id = int(input("\nEnter Teacher ID to unsuspend: "))

            # Check if teacher is suspended
            cursor.execute("SELECT name FROM teachers t JOIN teacher_status ts ON t.id = ts.teacher_id WHERE t.id = %s AND ts.status = 'suspended'", (teacher_id,))
            teacher = cursor.fetchone()

            if not teacher:
                print("Teacher not found or not suspended!")
                return

            # Update status to active
            cursor.execute("UPDATE teacher_status SET status = 'active', suspension_reason = NULL WHERE teacher_id = %s", (teacher_id,))

            self.connection.commit()
            print(f"Teacher {teacher['name']} unsuspended successfully!")

        except ValueError:
            print("Invalid teacher ID!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def remove_teacher(self):
        """Remove a teacher permanently"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show teachers who can be removed (not already removed)
            cursor.execute("""
            SELECT t.id, t.name, t.teaching_subject
            FROM teachers t
            LEFT JOIN teacher_status ts ON t.id = ts.teacher_id
            WHERE ts.status IS NULL OR ts.status != 'removed'
            ORDER BY t.name
            """)
            teachers = cursor.fetchall()

            if not teachers:
                print("No teachers available for removal.")
                return

            print("\nTeachers available for removal:")
            for teacher in teachers:
                print(f"{teacher['id']}. {teacher['name']} - {teacher['teaching_subject']}")

            teacher_id = int(input("\nEnter Teacher ID to remove: "))

            # Check if teacher exists and is not removed
            cursor.execute("""
            SELECT t.name FROM teachers t
            LEFT JOIN teacher_status ts ON t.id = ts.teacher_id
            WHERE t.id = %s AND (ts.status IS NULL OR ts.status != 'removed')
            """, (teacher_id,))
            teacher = cursor.fetchone()

            if not teacher:
                print("Teacher not found or already removed!")
                return

            confirm = input(f"Are you sure you want to remove teacher {teacher['name']}? This action cannot be undone! (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Removal cancelled.")
                return

            # Insert removal record
            cursor.execute("""
            INSERT INTO teacher_status (teacher_id, status, suspension_reason, suspended_by)
            VALUES (%s, 'removed', 'Administrative removal', %s)
            ON DUPLICATE KEY UPDATE
            status = 'removed', suspension_reason = 'Administrative removal', suspended_by = %s, suspended_at = CURRENT_TIMESTAMP
            """, (teacher_id, self.current_user['id'], self.current_user['id']))

            self.connection.commit()
            print(f"Teacher {teacher['name']} removed successfully!")

        except ValueError:
            print("Invalid teacher ID!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def view_suspended_teachers(self):
        """View suspended teachers"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT t.name, t.teaching_subject, ts.suspension_reason, ts.suspended_at, u.username as suspended_by
            FROM teachers t
            JOIN teacher_status ts ON t.id = ts.teacher_id
            LEFT JOIN users u ON ts.suspended_by = u.id
            WHERE ts.status = 'suspended'
            ORDER BY ts.suspended_at DESC
            """)
            teachers = cursor.fetchall()

            print("\n" + "="*50)
            print("        SUSPENDED TEACHERS")
            print("="*50)

            if not teachers:
                print("No suspended teachers found.")
                return

            for teacher in teachers:
                print(f"\nName: {teacher['name']}")
                print(f"Subject: {teacher['teaching_subject']}")
                print(f"Suspended: {teacher['suspended_at']}")
                print(f"Reason: {teacher['suspension_reason']}")
                print(f"Suspended by: {teacher['suspended_by'] or 'Unknown'}")
                print("-" * 40)

            print(f"\nTotal suspended teachers: {len(teachers)}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def view_removed_teachers(self):
        """View removed teachers"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT t.name, t.teaching_subject, ts.suspended_at, u.username as removed_by
            FROM teachers t
            JOIN teacher_status ts ON t.id = ts.teacher_id
            LEFT JOIN users u ON ts.suspended_by = u.id
            WHERE ts.status = 'removed'
            ORDER BY ts.suspended_at DESC
            """)
            teachers = cursor.fetchall()

            print("\n" + "="*50)
            print("        REMOVED TEACHERS")
            print("="*50)

            if not teachers:
                print("No removed teachers found.")
                return

            for teacher in teachers:
                print(f"\nName: {teacher['name']}")
                print(f"Subject: {teacher['teaching_subject']}")
                print(f"Removed: {teacher['suspended_at']}")
                print(f"Removed by: {teacher['removed_by'] or 'Unknown'}")
                print("-" * 40)

            print(f"\nTotal removed teachers: {len(teachers)}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def manage_subjects(self):
        """Admin: Manage subjects (view, add, delete, allot to students/classes)"""
        print("\n" + "="*50)
        print("        MANAGE SUBJECTS")
        print("="*50)
        print("1. View All Subjects")
        print("2. Add Subject")
        print("3. Delete Subject")
        print("4. Reassign Subject Teacher")
        print("5. Allot Subjects to Student")
        print("6. Allot Subjects to Class")

        choice = input("\nEnter choice (1-6): ").strip()

        if choice == '1':
            self.view_all_subjects()
        elif choice == '2':
            self.create_subject()
        elif choice == '3':
            self.delete_subject()
        elif choice == '4':
            self.reassign_subject_teacher()
        elif choice == '5':
            self.allot_subjects_to_student()
        elif choice == '6':
            self.allot_subjects_to_class()
        else:
            print("Invalid choice!")

    def edit_student_class_assignment(self):
        """Admin: Edit student class and section assignment"""
        print("\n" + "="*50)
        print("    EDIT STUDENT CLASS ASSIGNMENT")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show all students with their current class-section
            cursor.execute("""
            SELECT s.id, s.name, s.admission_number, c.class_name, c.section,
                   CASE WHEN ss.status IS NULL THEN 'active' ELSE ss.status END as status
            FROM students s
            JOIN classes c ON s.class_id = c.id
            LEFT JOIN student_status ss ON s.id = ss.student_id
            ORDER BY c.class_name, c.section, s.name
            """)

            students = cursor.fetchall()

            if not students:
                print("No students found.")
                return

            print("\nAvailable Students:")
            print("-" * 80)
            for student in students:
                status = student['status'].upper()
                print("{}. {} ({}) - Current: {}-{} [{}]".format(
                    student['id'], student['name'], student['admission_number'],
                    student['class_name'], student['section'], status))

            student_id = int(input("\nEnter Student ID to reassign: "))

            # Verify student exists
            cursor.execute("""
            SELECT s.name, s.admission_number, c.class_name, c.section
            FROM students s
            JOIN classes c ON s.class_id = c.id
            WHERE s.id = %s
            """, (student_id,))
            student = cursor.fetchone()

            if not student:
                print("Student not found!")
                return

            print(f"\nReassigning: {student['name']} ({student['admission_number']})")
            print(f"Current assignment: {student['class_name']}-{student['section']}")

            # Show available class names
            cursor.execute("SELECT DISTINCT class_name FROM classes ORDER BY class_name")
            class_names = cursor.fetchall()

            print("\nAvailable Class Names:")
            for i, cls in enumerate(class_names, 1):
                print("{}. {}".format(i, cls['class_name']))

            class_choice = int(input("\nSelect New Class Name (number): "))

            if class_choice < 1 or class_choice > len(class_names):
                print("Invalid class selection!")
                return

            selected_class_name = class_names[class_choice - 1]['class_name']

            # Show sections for selected class
            cursor.execute("SELECT id, section FROM classes WHERE class_name = %s ORDER BY section",
                         (selected_class_name,))
            sections = cursor.fetchall()

            print(f"\nAvailable Sections for {selected_class_name}:")
            for section in sections:
                print("{}. Section {}".format(section['id'], section['section']))

            new_class_id = int(input(f"\nSelect New Section ID for {selected_class_name}: "))

            # Verify the new class_id belongs to the selected class
            cursor.execute("SELECT id, class_name, section FROM classes WHERE id = %s", (new_class_id,))
            new_class_info = cursor.fetchone()

            if not new_class_info or new_class_info['class_name'] != selected_class_name:
                print("Invalid section selection!")
                return

            # Check if this is the same assignment
            if student['class_name'] == new_class_info['class_name'] and student['section'] == new_class_info['section']:
                print("Student is already assigned to this class-section!")
                return

            # Confirm reassignment
            confirm = input(f"\nReassign {student['name']} from {student['class_name']}-{student['section']} to {new_class_info['class_name']}-{new_class_info['section']}? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Reassignment cancelled.")
                return

            # Update student's class_id
            cursor.execute("UPDATE students SET class_id = %s WHERE id = %s", (new_class_id, student_id))

            # Remove old subject assignments
            cursor.execute("DELETE FROM student_subjects WHERE student_id = %s", (student_id,))

            # Auto-assign subjects from the new class-section
            cursor.execute("SELECT id, subject_name FROM subjects WHERE class_id = %s", (new_class_id,))
            new_subjects = cursor.fetchall()

            if new_subjects:
                for subject in new_subjects:
                    cursor.execute("""
                    INSERT INTO student_subjects (student_id, subject_id)
                    VALUES (%s, %s)
                    """, (student_id, subject['id']))

            # Commit all changes
            self.connection.commit()

            print("✓ Student reassignment completed successfully!")
            print(f"✓ Student {student['name']} moved to {new_class_info['class_name']}-{new_class_info['section']}")
            print(f"✓ Old subject assignments removed")
            print(f"✓ Auto-assigned {len(new_subjects)} new subjects")

        except ValueError:
            print("Invalid input! Please enter numbers for IDs.")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def view_all_subjects(self):
        """View all subjects with details"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT s.id, s.subject_name, c.class_name, c.section, t.name as teacher_name
            FROM subjects s
            JOIN classes c ON s.class_id = c.id
            LEFT JOIN teachers t ON s.teacher_id = t.id
            ORDER BY c.class_name, c.section, s.subject_name
            """)
            subjects = cursor.fetchall()

            print("\n" + "="*50)
            print("        ALL SUBJECTS")
            print("="*50)

            if not subjects:
                print("No subjects found.")
                return

            current_class = None
            for subject in subjects:
                class_display = f"{subject['class_name']}-{subject['section']}"
                if class_display != current_class:
                    current_class = class_display
                    print(f"\nClass: {current_class}")
                    print("-" * 40)

                teacher_name = subject['teacher_name'] if subject['teacher_name'] else "Not assigned"
                print(f"ID: {subject['id']} | Subject: {subject['subject_name']} | Teacher: {teacher_name}")

            print(f"\nTotal subjects: {len(subjects)}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def delete_subject(self):
        """Delete a subject"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show all subjects
            cursor.execute("""
            SELECT s.id, s.subject_name, c.class_name, c.section
            FROM subjects s
            JOIN classes c ON s.class_id = c.id
            ORDER BY c.class_name, c.section, s.subject_name
            """)
            subjects = cursor.fetchall()

            if not subjects:
                print("No subjects found.")
                return

            print("\nAvailable Subjects:")
            for subject in subjects:
                print(f"{subject['id']}. {subject['subject_name']} ({subject['class_name']}-{subject['section']})")

            subject_id = int(input("\nEnter Subject ID to delete: "))

            # Check if subject exists
            cursor.execute("SELECT subject_name FROM subjects WHERE id = %s", (subject_id,))
            subject = cursor.fetchone()
            if not subject:
                print("Subject not found!")
                return

            confirm = input(f"Are you sure you want to delete '{subject['subject_name']}'? (yes/no): ").strip().lower()
            if confirm != 'yes':
                print("Deletion cancelled.")
                return

            # Delete subject (this will cascade to related tables)
            cursor.execute("DELETE FROM subjects WHERE id = %s", (subject_id,))

            self.connection.commit()
            print("Subject deleted successfully!")

        except ValueError:
            print("Invalid subject ID!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def edit_teacher_assignments(self):
        """Admin: Edit existing teacher assignments (add/remove classes, sections, subjects)"""
        print("\n" + "="*50)
        print("      EDIT TEACHER ASSIGNMENTS")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show all teachers with their current assignments
            cursor.execute("""
            SELECT t.id, t.name, COUNT(ta.id) as assignment_count
            FROM teachers t
            LEFT JOIN teacher_assignments ta ON t.id = ta.teacher_id
            GROUP BY t.id, t.name
            ORDER BY t.name
            """)
            teachers = cursor.fetchall()

            if not teachers:
                print("No teachers found.")
                return

            print("\nTeachers and their current assignments:")
            for teacher in teachers:
                print(f"{teacher['id']}. {teacher['name']} - {teacher['assignment_count']} assignments")

            teacher_id = int(input("\nSelect Teacher ID to edit assignments: "))

            # Verify teacher exists
            cursor.execute("SELECT name FROM teachers WHERE id = %s", (teacher_id,))
            teacher = cursor.fetchone()
            if not teacher:
                print("Teacher not found!")
                return

            print(f"\nEditing assignments for: {teacher['name']}")

            while True:
                print("\n" + "-"*40)
                print("1. View Current Assignments")
                print("2. Add New Assignment")
                print("3. Remove Assignment")
                print("4. Back to Main Menu")

                choice = input("\nEnter choice (1-4): ").strip()

                if choice == '1':
                    # View current assignments
                    cursor.execute("""
                    SELECT ta.id, c.class_name, c.section, s.subject_name, ta.assigned_at
                    FROM teacher_assignments ta
                    JOIN classes c ON ta.class_id = c.id
                    JOIN subjects s ON ta.subject_id = s.id
                    WHERE ta.teacher_id = %s
                    ORDER BY c.class_name, c.section, s.subject_name
                    """, (teacher_id,))

                    assignments = cursor.fetchall()

                    if not assignments:
                        print("No assignments found for this teacher.")
                    else:
                        print(f"\nCurrent Assignments for {teacher['name']}:")
                        print("-" * 80)
                        for assignment in assignments:
                            print(f"ID: {assignment['id']} | {assignment['class_name']}-{assignment['section']} | {assignment['subject_name']} | Assigned: {assignment['assigned_at']}")

                elif choice == '2':
                    # Add new assignment
                    print("\nAdding new assignment...")

                    # Show available classes
                    cursor.execute("SELECT * FROM classes ORDER BY class_name, section")
                    classes = cursor.fetchall()

                    if not classes:
                        print("No classes available.")
                        continue

                    print("\nAvailable Classes:")
                    for cls in classes:
                        print(f"{cls['id']}. {cls['class_name']} - Section {cls['section']}")

                    class_id = int(input("\nSelect Class ID: "))

                    # Verify class exists
                    cursor.execute("SELECT class_name, section FROM classes WHERE id = %s", (class_id,))
                    class_info = cursor.fetchone()
                    if not class_info:
                        print("Class not found!")
                        continue

                    print(f"\nSelected: {class_info['class_name']}-{class_info['section']}")

                    # Show subjects for this class
                    cursor.execute("SELECT id, subject_name FROM subjects WHERE class_id = %s", (class_id,))
                    subjects = cursor.fetchall()

                    if not subjects:
                        print("No subjects found for this class.")
                        continue

                    print("\nAvailable Subjects:")
                    for subject in subjects:
                        print(f"{subject['id']}. {subject['subject_name']}")

                    subject_id = int(input("\nSelect Subject ID: "))

                    # Verify subject exists for this class
                    cursor.execute("SELECT subject_name FROM subjects WHERE id = %s AND class_id = %s", (subject_id, class_id))
                    subject = cursor.fetchone()
                    if not subject:
                        print("Subject not found for this class!")
                        continue

                    # Check if assignment already exists
                    cursor.execute("SELECT id FROM teacher_assignments WHERE teacher_id = %s AND class_id = %s AND subject_id = %s",
                                 (teacher_id, class_id, subject_id))
                    existing = cursor.fetchone()

                    if existing:
                        print("Assignment already exists!")
                        continue

                    # Create assignment
                    cursor.execute("INSERT INTO teacher_assignments (teacher_id, class_id, subject_id, assigned_by) VALUES (%s, %s, %s, %s)",
                                 (teacher_id, class_id, subject_id, self.current_user['id']))

                    # Update subjects table
                    cursor.execute("UPDATE subjects SET teacher_id = %s WHERE id = %s", (teacher_id, subject_id))

                    self.connection.commit()
                    print("✓ Assignment added successfully!")

                elif choice == '3':
                    # Remove assignment
                    print("\nRemoving assignment...")

                    # Show current assignments
                    cursor.execute("""
                    SELECT ta.id, c.class_name, c.section, s.subject_name
                    FROM teacher_assignments ta
                    JOIN classes c ON ta.class_id = c.id
                    JOIN subjects s ON ta.subject_id = s.id
                    WHERE ta.teacher_id = %s
                    ORDER BY c.class_name, c.section, s.subject_name
                    """, (teacher_id,))

                    assignments = cursor.fetchall()

                    if not assignments:
                        print("No assignments found for this teacher.")
                        continue

                    print(f"\nCurrent Assignments for {teacher['name']}:")
                    for assignment in assignments:
                        print(f"{assignment['id']}. {assignment['class_name']}-{assignment['section']} - {assignment['subject_name']}")

                    assignment_id = int(input("\nEnter Assignment ID to remove: "))

                    # Verify assignment exists and belongs to this teacher
                    cursor.execute("SELECT class_id, subject_id FROM teacher_assignments WHERE id = %s AND teacher_id = %s",
                                 (assignment_id, teacher_id))
                    assignment = cursor.fetchone()
                    if not assignment:
                        print("Assignment not found!")
                        continue

                    confirm = input("Are you sure you want to remove this assignment? (yes/no): ").strip().lower()
                    if confirm != 'yes':
                        print("Removal cancelled.")
                        continue

                    # Remove assignment
                    cursor.execute("DELETE FROM teacher_assignments WHERE id = %s", (assignment_id,))

                    # Check if teacher still has other assignments for this subject
                    cursor.execute("SELECT id FROM teacher_assignments WHERE teacher_id = %s AND subject_id = %s",
                                 (teacher_id, assignment['subject_id']))
                    other_assignments = cursor.fetchone()

                    # If no other assignments for this subject, remove teacher from subjects table
                    if not other_assignments:
                        cursor.execute("UPDATE subjects SET teacher_id = NULL WHERE id = %s", (assignment['subject_id'],))

                    self.connection.commit()
                    print("✓ Assignment removed successfully!")

                elif choice == '4':
                    break
                else:
                    print("Invalid choice!")

        except ValueError:
            print("Invalid input! Please enter numbers for IDs.")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def view_teacher_profile(self):
        """Teacher: View own profile and login details"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT t.*, u.username, COUNT(tr.id) as record_count, tp.*
            FROM teachers t
            JOIN users u ON t.user_id = u.id
            LEFT JOIN teaching_records tr ON t.id = tr.teacher_id
            LEFT JOIN teacher_privileges tp ON t.id = tp.teacher_id
            WHERE t.user_id = %s
            GROUP BY t.id
            """, (self.current_user['id'],))

            teacher = cursor.fetchone()

            if not teacher:
                print("Teacher profile not found!")
                return

            print("\n" + "="*50)
            print("        MY PROFILE & LOGIN DETAILS")
            print("="*50)

            print(f"Name: {teacher['name']}")
            print(f"Username: {teacher['username']}")
            print(f"Password: teacher123 (default - change recommended)")
            print(f"Age: {teacher['age']}")
            print(f"Subject: {teacher['teaching_subject']}")
            print(f"Qualifications: {teacher['highest_qualifications']}")
            print(f"Teaching Records: {teacher['record_count']}")

            print(f"\nPrivileges:")
            print(f"  Can Edit Students: {'Yes' if teacher.get('can_edit_students') else 'No'}")
            print(f"  Can Delete Students: {'Yes' if teacher.get('can_delete_students') else 'No'}")
            print(f"  Can Suspend Students: {'Yes' if teacher.get('can_suspend_students') else 'No'}")
            print(f"  Can Edit Subjects: {'Yes' if teacher.get('can_edit_subjects') else 'No'}")
            print(f"  Can Delete Subjects: {'Yes' if teacher.get('can_delete_subjects') else 'No'}")
            print(f"  Can Edit Attendance: {'Yes' if teacher.get('can_edit_attendance') else 'No'}")

            print(f"\nDate of Birth: {teacher['dob']}")
            print(f"Created: {teacher['created_at']}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def teacher_manage_student_status(self):
        """Teacher: Manage student status (limited by privileges)"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Check teacher privileges
            cursor.execute("SELECT * FROM teacher_privileges WHERE teacher_id = (SELECT id FROM teachers WHERE user_id = %s)", (self.current_user['id'],))
            priv = cursor.fetchone()

            if not priv or not priv['can_suspend_students']:
                print("You don't have permission to manage student status.")
                return

            print("\n" + "="*50)
            print("    TEACHER: MANAGE STUDENT STATUS")
            print("="*50)
            print("1. Suspend Student")
            print("2. Unsuspend Student")

            choice = input("\nEnter choice (1-2): ").strip()

            if choice == '1':
                self.teacher_suspend_student()
            elif choice == '2':
                self.teacher_unsuspend_student()
            else:
                print("Invalid choice!")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def teacher_suspend_student(self):
        """Teacher: Suspend a student from assigned classes only"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Check teacher privileges
            cursor.execute("SELECT can_suspend_students FROM teacher_privileges WHERE teacher_id = (SELECT id FROM teachers WHERE user_id = %s)", (self.current_user['id'],))
            priv = cursor.fetchone()

            if not priv or not priv['can_suspend_students']:
                print("You don't have permission to suspend students.")
                return

            # Get teacher's assigned classes
            cursor.execute("""
            SELECT DISTINCT c.id, c.class_name, c.section
            FROM teacher_assignments ta
            JOIN classes c ON ta.class_id = c.id
            WHERE ta.teacher_id = (SELECT id FROM teachers WHERE user_id = %s)
            ORDER BY c.class_name, c.section
            """, (self.current_user['id'],))

            classes = cursor.fetchall()

            if not classes:
                print("You have no assigned classes.")
                return

            print("\nYour Assigned Classes:")
            for cls in classes:
                print(f"{cls['id']}. {cls['class_name']} - Section {cls['section']}")

            class_id = int(input("\nSelect Class ID: "))

            # Verify this class is assigned to the teacher
            cursor.execute("""
            SELECT c.class_name, c.section FROM classes c
            JOIN teacher_assignments ta ON ta.class_id = c.id
            WHERE c.id = %s AND ta.teacher_id = (SELECT id FROM teachers WHERE user_id = %s)
            """, (class_id, self.current_user['id']))

            assigned_class = cursor.fetchone()
            if not assigned_class:
                print("You are not assigned to this class!")
                return

            # Get active students from assigned class only
            cursor.execute("""
            SELECT s.id, s.name, s.admission_number
            FROM students s
            LEFT JOIN student_status ss ON s.id = ss.student_id
            WHERE s.class_id = %s AND (ss.status IS NULL OR ss.status = 'active')
            ORDER BY s.name
            """, (class_id,))

            students = cursor.fetchall()

            if not students:
                print("No active students in this assigned class.")
                return

            print(f"\nActive Students in {assigned_class['class_name']}-{assigned_class['section']}:")
            for student in students:
                print(f"{student['id']}. {student['name']} ({student['admission_number']})")

            student_id = int(input("\nEnter Student ID to suspend: "))
            reason = input("Suspension reason: ").strip()

            if not reason:
                reason = "Teacher suspension"

            # Verify student is in teacher's assigned class
            cursor.execute("SELECT name FROM students WHERE id = %s AND class_id = %s", (student_id, class_id))
            student = cursor.fetchone()

            if not student:
                print("Student not found in your assigned class!")
                return

            # Insert suspension record
            cursor.execute("""
            INSERT INTO student_status (student_id, status, suspension_reason, suspended_by)
            VALUES (%s, 'suspended', %s, %s)
            ON DUPLICATE KEY UPDATE
            status = 'suspended', suspension_reason = %s, suspended_by = %s, suspended_at = CURRENT_TIMESTAMP
            """, (student_id, reason, self.current_user['id'], reason, self.current_user['id']))

            self.connection.commit()
            print(f"✓ Student {student['name']} suspended successfully from {assigned_class['class_name']}-{assigned_class['section']}!")

        except ValueError:
            print("Invalid input!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def teacher_unsuspend_student(self):
        """Teacher: Unsuspend a student from assigned classes only"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Check teacher privileges
            cursor.execute("SELECT can_suspend_students FROM teacher_privileges WHERE teacher_id = (SELECT id FROM teachers WHERE user_id = %s)", (self.current_user['id'],))
            priv = cursor.fetchone()

            if not priv or not priv['can_suspend_students']:
                print("You don't have permission to manage student suspensions.")
                return

            # Get teacher's assigned classes
            cursor.execute("""
            SELECT DISTINCT c.id, c.class_name, c.section
            FROM teacher_assignments ta
            JOIN classes c ON ta.class_id = c.id
            WHERE ta.teacher_id = (SELECT id FROM teachers WHERE user_id = %s)
            ORDER BY c.class_name, c.section
            """, (self.current_user['id'],))

            classes = cursor.fetchall()

            if not classes:
                print("You have no assigned classes.")
                return

            print("\nYour Assigned Classes:")
            for cls in classes:
                print(f"{cls['id']}. {cls['class_name']} - Section {cls['section']}")

            class_id = int(input("\nSelect Class ID: "))

            # Verify this class is assigned to the teacher
            cursor.execute("""
            SELECT c.class_name, c.section FROM classes c
            JOIN teacher_assignments ta ON ta.class_id = c.id
            WHERE c.id = %s AND ta.teacher_id = (SELECT id FROM teachers WHERE user_id = %s)
            """, (class_id, self.current_user['id']))

            assigned_class = cursor.fetchone()
            if not assigned_class:
                print("You are not assigned to this class!")
                return

            # Get suspended students from assigned class only (with student subjects for segregation)
            cursor.execute("""
            SELECT DISTINCT s.id, s.name, s.admission_number, ss.suspension_reason
            FROM students s
            JOIN student_status ss ON s.id = ss.student_id
            JOIN student_subjects sts ON s.id = sts.student_id
            JOIN subjects sub ON sts.subject_id = sub.id
            WHERE s.class_id = %s AND ss.status = 'suspended'
            AND sub.class_id = %s
            ORDER BY s.name
            """, (class_id, class_id))

            students = cursor.fetchall()

            if not students:
                print("No suspended students in this assigned class.")
                return

            print(f"\nSuspended Students in {assigned_class['class_name']}-{assigned_class['section']}:")
            for student in students:
                print(f"{student['id']}. {student['name']} ({student['admission_number']}) - Reason: {student['suspension_reason']}")

            student_id = int(input("\nEnter Student ID to unsuspend: "))

            # Verify student is suspended in teacher's assigned class
            cursor.execute("""
            SELECT s.name FROM students s
            JOIN student_status ss ON s.id = ss.student_id
            WHERE s.id = %s AND s.class_id = %s AND ss.status = 'suspended'
            """, (student_id, class_id))

            student = cursor.fetchone()

            if not student:
                print("Student not found or not suspended in your assigned class!")
                return

            # Update status to active
            cursor.execute("UPDATE student_status SET status = 'active', suspension_reason = NULL WHERE student_id = %s", (student_id,))

            self.connection.commit()
            print(f"✓ Student {student['name']} unsuspended successfully from {assigned_class['class_name']}-{assigned_class['section']}!")

        except ValueError:
            print("Invalid input!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def view_teacher_assigned_classes(self):
        """Teacher: View assigned classes and subjects with student counts"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT DISTINCT c.class_name, c.section,
                   COUNT(DISTINCT s.id) as student_count,
                   COUNT(DISTINCT sub.id) as subject_count
            FROM teacher_assignments ta
            JOIN classes c ON ta.class_id = c.id
            LEFT JOIN students s ON c.id = s.class_id
            LEFT JOIN student_status ss ON s.id = ss.student_id AND ss.status = 'removed'
            LEFT JOIN subjects sub ON ta.subject_id = sub.id
            WHERE ta.teacher_id = (SELECT id FROM teachers WHERE user_id = %s)
            AND ss.id IS NULL
            GROUP BY c.class_name, c.section
            ORDER BY c.class_name, c.section
            """, (self.current_user['id'],))

            class_summary = cursor.fetchall()

            print("\n" + "="*50)
            print("        MY ASSIGNED CLASSES & SUBJECTS")
            print("="*50)

            if not class_summary:
                print("No class assignments found.")
                return

            total_students = 0
            total_subjects = 0

            for class_info in class_summary:
                print(f"\nClass: {class_info['class_name']}-{class_info['section']}")
                print(f"Students: {class_info['student_count']}")
                print(f"Subjects: {class_info['subject_count']}")
                print("-" * 40)

                total_students += class_info['student_count']
                total_subjects += class_info['subject_count']

                # Show subjects for this class
                cursor.execute("""
                SELECT s.subject_name, ta.assigned_at
                FROM teacher_assignments ta
                JOIN subjects s ON ta.subject_id = s.id
                JOIN classes c ON ta.class_id = c.id
                WHERE ta.teacher_id = (SELECT id FROM teachers WHERE user_id = %s)
                AND c.class_name = %s AND c.section = %s
                ORDER BY s.subject_name
                """, (self.current_user['id'], class_info['class_name'], class_info['section']))

                subjects = cursor.fetchall()
                for subject in subjects:
                    print(f"  • {subject['subject_name']} (Assigned: {subject['assigned_at']})")

            print(f"\n{'='*50}")
            print(f"Summary: {len(class_summary)} classes | {total_subjects} subjects | {total_students} students")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def view_all_teachers(self):
        """View all teachers with their privileges"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT t.*, COUNT(tr.id) as record_count,
                   tp.can_edit_students, tp.can_delete_students, tp.can_suspend_students,
                   tp.can_edit_subjects, tp.can_delete_subjects, tp.can_edit_attendance
            FROM teachers t
            LEFT JOIN teaching_records tr ON t.id = tr.teacher_id
            LEFT JOIN teacher_privileges tp ON t.id = tp.teacher_id
            GROUP BY t.id, tp.can_edit_students, tp.can_delete_students, tp.can_suspend_students,
                     tp.can_edit_subjects, tp.can_delete_subjects, tp.can_edit_attendance
            ORDER BY t.name
            """)
            teachers = cursor.fetchall()

            print("\n" + "="*50)
            print("        ALL TEACHERS & PRIVILEGES")
            print("="*50)

            for teacher in teachers:
                print(f"\nID: {teacher['id']}")
                print(f"Name: {teacher['name']}")
                print(f"Age: {teacher['age']}")
                print(f"Subject: {teacher['teaching_subject']}")
                print(f"Qualifications: {teacher['highest_qualifications']}")
                print(f"Teaching Records: {teacher['record_count']}")

                print("Privileges:")
                print(f"  Edit Students: {'Yes' if teacher.get('can_edit_students') else 'No'}")
                print(f"  Delete Students: {'Yes' if teacher.get('can_delete_students') else 'No'}")
                print(f"  Suspend Students: {'Yes' if teacher.get('can_suspend_students') else 'No'}")
                print(f"  Edit Subjects: {'Yes' if teacher.get('can_edit_subjects') else 'No'}")
                print(f"  Delete Subjects: {'Yes' if teacher.get('can_delete_subjects') else 'No'}")
                print(f"  Edit Attendance: {'Yes' if teacher.get('can_edit_attendance') else 'No'}")
                print("-" * 40)

            print(f"\nTotal Teachers: {len(teachers)}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()


    def principal_view_timetables(self):
        """Principal: View all timetables"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT tt.day_of_week, tt.lecture_number, tt.start_time, tt.end_time,
                   s.subject_name, c.class_name, c.section, t.name as teacher_name
            FROM timetable tt
            JOIN subjects s ON tt.subject_id = s.id
            JOIN classes c ON tt.class_id = c.id
            JOIN teachers t ON tt.teacher_id = t.id
            ORDER BY
                FIELD(tt.day_of_week, 'monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday'),
                tt.lecture_number, c.class_name, c.section
            """)

            timetable = cursor.fetchall()

            print("\n" + "="*80)
            print("                SCHOOL TIMETABLE")
            print("="*80)

            if not timetable:
                print("No timetable entries found.")
                return

            current_day = None
            current_class = None

            for entry in timetable:
                class_display = f"{entry['class_name']}-{entry['section']}"
                if entry['day_of_week'] != current_day:
                    current_day = entry['day_of_week']
                    print(f"\n{current_day.upper()}:")
                    print("-" * 80)
                    current_class = None

                if class_display != current_class:
                    current_class = class_display
                    print(f"\nClass: {current_class}")
                    print("-" * 60)

                print(f"  Lecture {entry['lecture_number']}: {entry['start_time']} - {entry['end_time']}")
                print(f"  Subject: {entry['subject_name']} | Teacher: {entry['teacher_name']}")
                print()

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def principal_view_teacher_assignments(self):
        """Principal: View all teacher assignments"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT t.name, ta.class_id, c.class_name, c.section, s.subject_name
            FROM teacher_assignments ta
            JOIN teachers t ON ta.teacher_id = t.id
            JOIN classes c ON ta.class_id = c.id
            JOIN subjects s ON ta.subject_id = s.id
            ORDER BY t.name, c.class_name, c.section
            """)

            assignments = cursor.fetchall()

            print("\n" + "="*50)
            print("        TEACHER ASSIGNMENTS")
            print("="*50)

            if not assignments:
                print("No teacher assignments found.")
                return

            current_teacher = None
            for assignment in assignments:
                if assignment['name'] != current_teacher:
                    current_teacher = assignment['name']
                    print(f"\nTeacher: {current_teacher}")
                    print("-" * 40)

                print(f"  {assignment['class_name']}-{assignment['section']} - {assignment['subject_name']}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def principal_view_student_status(self):
        """Principal: View student status summary"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT c.class_name, c.section,
                   COUNT(s.id) as total_students,
                   SUM(CASE WHEN ss.status IS NULL OR ss.status = 'active' THEN 1 ELSE 0 END) as active_students,
                   SUM(CASE WHEN ss.status = 'suspended' THEN 1 ELSE 0 END) as suspended_students,
                   SUM(CASE WHEN ss.status = 'removed' THEN 1 ELSE 0 END) as removed_students
            FROM classes c
            LEFT JOIN students s ON c.id = s.class_id
            LEFT JOIN student_status ss ON s.id = ss.student_id
            GROUP BY c.class_name, c.section
            ORDER BY c.class_name, c.section
            """)

            status_summary = cursor.fetchall()

            print("\n" + "="*50)
            print("        STUDENT STATUS SUMMARY")
            print("="*50)

            if not status_summary:
                print("No class data found.")
                return

            total_active = 0
            total_suspended = 0
            total_removed = 0
            total_students = 0

            for summary in status_summary:
                active = summary['active_students'] or 0
                suspended = summary['suspended_students'] or 0
                removed = summary['removed_students'] or 0
                total_class = summary['total_students'] or 0

                total_active += active
                total_suspended += suspended
                total_removed += removed
                total_students += total_class

                print(f"\nClass: {summary['class_name']}-{summary['section']}")
                print(f"  Total Students: {total_class}")
                print(f"  Active: {active} | Suspended: {suspended} | Removed: {removed}")

            print(f"\n{'='*50}")
            print("OVERALL SUMMARY:")
            print(f"Total Students: {total_students}")
            print(f"Active: {total_active} | Suspended: {total_suspended} | Removed: {total_removed}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def academic_coordinator_dashboard(self):
        """
        Display and handle the academic coordinator dashboard.

        Provides menu options for academic planning and curriculum management
        including viewing subjects, teacher assignments, timetables, and
        academic performance analytics. Supports curriculum oversight and
        academic coordination functions. Runs in a loop until logout.

        Menu Options:
            1. View All Subjects - Curriculum overview
            2. View Teacher Assignments - Assignment tracking
            3. View Timetables - Schedule management
            4. View Academic Performance - Analytics (under development)
            5. Logout

        Note:
            Focused on academic administration and curriculum development.
            Some features may be under development or require additional modules.
        """
        while True:
            print("\n" + "="*50)
            print("      ACADEMIC COORDINATOR DASHBOARD")
            print("="*50)
            print("Academic Planning and Curriculum Management")
            print("1.  View All Subjects")
            print("2.  View Teacher Assignments")
            print("3.  View Timetables")
            print("4.  View Academic Performance")
            print("5.  Logout")

            choice = input("\nEnter your choice (1-5): ").strip()

            if choice == '1':
                self.view_all_subjects()
            elif choice == '2':
                self.principal_view_teacher_assignments()
            elif choice == '3':
                self.principal_view_timetables()
            elif choice == '4':
                print("Academic performance analysis - Under development")
            elif choice == '5':
                self.logout()
                break
            else:
                print("Invalid choice! Please try again.")

    def admission_department_dashboard(self):
        """
        Display and handle the admission department dashboard.

        Provides menu options for student admissions and enrollment management
        including viewing students, class capacities, and admission statistics.
        Supports enrollment tracking and capacity planning. Runs in a loop until logout.

        Menu Options:
            1. View All Students - Enrollment overview
            2. View Class Capacities - Capacity management
            3. View Admission Statistics - Enrollment stats
            4. Logout

        Note:
            Focused on student admissions and enrollment tracking.
            Provides data for admission planning and capacity management.
        """
        while True:
            print("\n" + "="*50)
            print("       ADMISSION DEPARTMENT DASHBOARD")
            print("="*50)
            print("Student Admissions and Enrollment")
            print("1.  View All Students")
            print("2.  View Class Capacities")
            print("3.  View Admission Statistics")
            print("4.  Logout")

            choice = input("\nEnter your choice (1-4): ").strip()

            if choice == '1':
                self.view_all_students()
            elif choice == '2':
                self.view_all_classes()
            elif choice == '3':
                self.principal_view_student_status()
            elif choice == '4':
                self.logout()
                break
            else:
                print("Invalid choice! Please try again.")

    def view_all_students(self):
        """View all students with their status"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT s.*, c.class_name, c.section,
                   CASE WHEN ss.status IS NULL THEN 'active' ELSE ss.status END as status
            FROM students s
            JOIN classes c ON s.class_id = c.id
            LEFT JOIN student_status ss ON s.id = ss.student_id
            ORDER BY c.class_name, c.section, s.name
            """)
            students = cursor.fetchall()

            print("\n" + "="*50)
            print("        ALL STUDENTS & STATUS")
            print("="*50)

            status_counts = {'active': 0, 'suspended': 0, 'removed': 0}

            current_class = None
            for student in students:
                class_display = f"{student['class_name']}-{student['section']}"
                if class_display != current_class:
                    current_class = class_display
                    print(f"\nClass: {current_class}")
                    print("-" * 40)

                status = student['status'].upper()
                status_counts[student['status']] += 1
                print(f"Admission No: {student['admission_number']}")
                print(f"Name: {student['name']}")
                print(f"Status: {status}")
                print(f"Father: {student['father_name']} ({student['father_occupation']})")
                print(f"Mother: {student['mother_name']} ({student['mother_occupation']})")
                print(f"Contact: {student['contact_number']}")
                print("-" * 30)

            print(f"\nTotal Students: {len(students)}")
            print(f"Active: {status_counts['active']} | Suspended: {status_counts['suspended']} | Removed: {status_counts['removed']}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def view_student_subjects(self):
        """View student's subjects"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT s.subject_name, t.name as teacher_name
            FROM subjects s
            JOIN teachers t ON s.teacher_id = t.id
            WHERE s.class_id = (SELECT class_id FROM students WHERE user_id = %s)
            ORDER BY s.subject_name
            """, (self.current_user['id'],))

            subjects = cursor.fetchall()

            print("\n" + "="*50)
            print("            YOUR SUBJECTS")
            print("="*50)

            if not subjects:
                print("No subjects found.")
                return

            for subject in subjects:
                print(f"Subject: {subject['subject_name']}")
                print(f"Teacher: {subject['teacher_name']}")
                print("-" * 30)

            print(f"\nTotal Subjects: {len(subjects)}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()
    
    def view_student_profile(self):
        """View student's profile"""
        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            cursor.execute("""
            SELECT s.*, c.class_name, c.section
            FROM students s
            JOIN classes c ON s.class_id = c.id
            WHERE s.user_id = %s
            """, (self.current_user['id'],))

            student = cursor.fetchone()

            if not student:
                print("Student profile not found!")
                return

            print("\n" + "="*50)
            print("            YOUR PROFILE")
            print("="*50)

            print(f"Admission Number: {student['admission_number']}")
            print(f"Name: {student['name']}")
            print(f"Username: {self.current_user['username']}")
            print(f"Password: [HIDDEN] (use option 5 to change)")
            print(f"Age: {student['age']}")
            print(f"Date of Birth: {student['dob']}")
            print(f"Class: {student['class_name']}-{student['section']}")
            print(f"Previous School: {student['previous_school']}")
            print(f"\nParent Details:")
            print(f"  Father: {student['father_name']} ({student['father_occupation']})")
            print(f"  Mother: {student['mother_name']} ({student['mother_occupation']})")
            print(f"  Contact: {student['contact_number']}")
            print(f"  Emergency Contact: {student['emergency_contact']}")

        except pymysql.Error as err:
            print(f"Database error: {err}")
        finally:
            cursor.close()

    def change_student_credentials(self):
        """Student: Change username and password"""
        print("\n" + "="*50)
        print("        CHANGE USERNAME & PASSWORD")
        print("="*50)

        cursor = self.connection.cursor()

        try:
            print("Note: Name cannot be changed. Only admin can change names.")
            print("Leave fields empty to keep current values.")

            # Change username
            current_username = None
            cursor.execute("SELECT username FROM users WHERE id = %s", (self.current_user['id'],))
            result = cursor.fetchone()
            if result:
                current_username = result[0]

            new_username = input(f"New Username (current: {current_username}): ").strip()

            if new_username and new_username != current_username:
                # Check if new username already exists
                cursor.execute("SELECT id FROM users WHERE username = %s AND id != %s", (new_username, self.current_user['id']))
                if cursor.fetchone():
                    print("Username already exists! Please choose a different username.")
                    return

                # Update username
                cursor.execute("UPDATE users SET username = %s WHERE id = %s", (new_username, self.current_user['id']))
                self.current_user['username'] = new_username
                print("✓ Username updated successfully!")
            elif new_username == current_username:
                print("Username is the same as current.")
            else:
                print("Username not changed.")

            # Change password
            new_password = input("New Password (leave empty to keep current): ").strip()

            if new_password:
                confirm_password = input("Confirm New Password: ").strip()
                if new_password != confirm_password:
                    print("Passwords do not match!")
                    return

                hashed_password = self.hash_password(new_password)
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, self.current_user['id']))
                print("✓ Password updated successfully!")
            else:
                print("Password not changed.")

            self.connection.commit()

        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()
    
    def principal_dashboard(self):
        """
        Display and handle the principal dashboard menu with read-only access.

        Provides comprehensive read-only access to all school data for oversight
        and reporting purposes. Principals can view student/teacher information,
        attendance records, timetables, assignments, and status summaries without
        modification capabilities. Operates in a loop until logout.

        Menu Options:
            1-4: View all users, teachers, students, classes
            5-9: View attendance records, timetables, assignments, status summaries
            10. Logout

        Note:
            This role provides supervisory access without data modification rights.
            All data is presented in summary and detail formats for administrative review.
        """
        while True:
            print("\n" + "="*50)
            print("            PRINCIPAL DASHBOARD")
            print("="*50)
            print("READ-ONLY ACCESS - View all school data")
            print("1.  View All Students")
            print("2.  View All Teachers")
            print("3.  View All Classes")
            print("4.  View All Subjects")
            print("5.  View Student Attendance Records")
            print("6.  View Teacher Attendance Records")
            print("7.  View Timetables")
            print("8.  View Teacher Assignments")
            print("9.  View Student Status Summary")
            print("10. Logout")

            choice = input("\nEnter your choice (1-10): ").strip()

            if choice == '1':
                self.view_all_students()
            elif choice == '2':
                self.view_all_teachers()
            elif choice == '3':
                self.view_all_classes()
            elif choice == '4':
                self.view_all_subjects()
            elif choice == '5':
                self.view_attendance_records()
            elif choice == '6':
                self.view_attendance_records()
            elif choice == '7':
                self.principal_view_timetables()
            elif choice == '8':
                self.principal_view_teacher_assignments()
            elif choice == '9':
                self.principal_view_student_status()
            elif choice == '10':
                self.logout()
                break
            else:
                print("Invalid choice! Please try again.")
    
    def system_admin_dashboard(self):
        """System Administrator role dashboard"""
        print("\nSystem Administrator dashboard - Under development")
        # Technical operations like database maintenance
    
    def academic_coordinator_dashboard(self):
        """Academic Coordinator role dashboard"""
        print("\nAcademic Coordinator dashboard - Under development")
        # Curriculum management, academic planning
    
    def run(self):
        """
        Main application entry point and program loop.

        Displays the welcome message and manages the primary application workflow,
        including user authentication, role-based dashboard routing, and graceful
        exit handling. The application runs in a continuous loop until explicitly
        terminated by the user.

        Program Flow:
            1. Display system welcome and role information
            2. Present login/exit options when user is not authenticated
            3. Route authenticated users to role-specific dashboards
            4. Handle logout events and return to authentication loop
            5. Ensure proper database connection cleanup on exit

        Supported Roles:
            - admin: Full administrative access
            - teacher: Teaching and student management
            - student: Personal profile and attendance viewing
            - principal: Read-only access to all school data
            - academic_coordinator: Curriculum and subject management
            - admission_department: Student enrollment tracking

        Note:
            The application uses a state-based loop structure where authentication
            state determines available options. All database operations are properly
            wrapped with error handling and transaction management.
        """
        print("="*60)
        print("      SCHOOL MANAGEMENT SYSTEM")
        print("="*60)
        print("Developed for CBSE Curriculum")
        print("Roles: Admin, Teacher, Student, Principal, System Admin, Academic Coordinator")
        
        while True:
            if not self.current_user:
                # Not logged in - show login options
                print("\n1. Login")
                print("2. Exit")
                
                choice = input("\nEnter choice (1-2): ").strip()
                
                if choice == '1':
                    if self.login():
                        # Redirect to appropriate dashboard based on role
                        if self.current_role == 'admin':
                            self.admin_dashboard()
                        elif self.current_role == 'teacher':
                            self.teacher_dashboard()
                        elif self.current_role == 'student':
                            self.student_dashboard()
                        elif self.current_role == 'principal':
                            self.principal_dashboard()
                        elif self.current_role == 'system_admin':
                            self.system_admin_dashboard()
                        elif self.current_role == 'academic_coordinator':
                            self.academic_coordinator_dashboard()
                elif choice == '2':
                    print("\nThank you for using School Management System!")
                    if self.connection:
                        self.connection.close()
                    break
                else:
                    print("Invalid choice! Please try again.")
            else:
                # Already logged in - this shouldn't happen due to dashboard loops
                self.current_user = None

    def edit_user_details(self):
        """Admin: Edit user details (username, password, name, etc.)"""
        print("\n" + "="*50)
        print("        EDIT USER DETAILS")
        print("="*50)

        cursor = self.connection.cursor(pymysql.cursors.DictCursor)

        try:
            # Show all users
            cursor.execute("""
            SELECT u.id, u.username, u.role,
                   CASE WHEN u.role = 'student' THEN s.name
                        WHEN u.role IN ('teacher', 'principal', 'academic_coordinator', 'admission_department') THEN t.name
                        ELSE 'N/A' END as name
            FROM users u
            LEFT JOIN students s ON u.id = s.user_id
            LEFT JOIN teachers t ON u.id = t.user_id
            ORDER BY u.role, u.username
            """)

            users = cursor.fetchall()

            if not users:
                print("No users found.")
                return

            print("\nAvailable Users:")
            print("-" * 80)
            for user in users:
                print(f"{user['id']}. {user['username']} ({user['role']}) - {user['name']}")

            user_id = int(input("\nEnter User ID to edit: "))

            # Verify user exists
            user_info = next((u for u in users if u['id'] == user_id), None)
            if not user_info:
                print("User not found!")
                return

            print(f"\nEditing user: {user_info['username']} ({user_info['role']})")

            # Get current details
            if user_info['role'] == 'student':
                cursor.execute("SELECT * FROM students WHERE user_id = %s", (user_id,))
                details = cursor.fetchone()
            elif user_info['role'] in ('teacher', 'principal', 'academic_coordinator', 'admission_department'):
                cursor.execute("SELECT * FROM teachers WHERE user_id = %s", (user_id,))
                details = cursor.fetchone()
            else:
                print("Cannot edit this user type.")
                return

            # Edit username
            new_username = input(f"Username (current: {user_info['username']}): ").strip()
            if new_username and new_username != user_info['username']:
                # Check uniqueness
                cursor.execute("SELECT id FROM users WHERE username = %s AND id != %s", (new_username, user_id))
                if cursor.fetchone():
                    print("Username already exists!")
                    return
                cursor.execute("UPDATE users SET username = %s WHERE id = %s", (new_username, user_id))
                print("✓ Username updated")

            # Edit password
            new_password = input("New Password (leave empty to keep current): ").strip()
            if new_password:
                hashed_password = self.hash_password(new_password)
                cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_password, user_id))
                print("✓ Password updated")

            # Edit name (only if not student/teacher - wait, admin can edit names)
            if details:
                new_name = input(f"Name (current: {details.get('name', 'N/A')}): ").strip()
                if new_name and new_name != details.get('name'):
                    if user_info['role'] == 'student':
                        cursor.execute("UPDATE students SET name = %s WHERE user_id = %s", (new_name, user_id))
                    else:
                        cursor.execute("UPDATE teachers SET name = %s WHERE user_id = %s", (new_name, user_id))
                    print("✓ Name updated")

                # Edit age and DOB for teachers/students
                if 'age' in details:
                    # For age, we need to recalculate from DOB
                    current_dob = details.get('dob', '')
                    new_dob_input = input(f"Date of Birth (YYYY-MM-DD) (current: {current_dob}): ").strip()
                    if new_dob_input:
                        try:
                            new_dob = datetime.strptime(new_dob_input, '%Y-%m-%d').date()
                            today = date.today()
                            new_age = today.year - new_dob.year - ((today.month, today.day) < (new_dob.month, new_dob.day))

                            if user_info['role'] == 'student':
                                cursor.execute("UPDATE students SET dob = %s, age = %s WHERE user_id = %s",
                                             (new_dob, new_age, user_id))
                            else:
                                cursor.execute("UPDATE teachers SET dob = %s, age = %s WHERE user_id = %s",
                                             (new_dob, new_age, user_id))
                            print("✓ DOB and Age updated")
                        except ValueError:
                            print("Invalid date format!")

                # Edit other fields based on role
                if user_info['role'] == 'student':
                    # Student-specific fields
                    fields_to_edit = {
                        'previous_school': 'Previous School',
                        'father_name': 'Father Name',
                        'mother_name': 'Mother Name',
                        'father_occupation': 'Father Occupation',
                        'mother_occupation': 'Mother Occupation',
                        'contact_number': 'Contact Number',
                        'emergency_contact': 'Emergency Contact'
                    }

                    for field, label in fields_to_edit.items():
                        current_value = details.get(field, '')
                        new_value = input(f"{label} (current: {current_value}): ").strip()
                        if new_value and new_value != current_value:
                            # Validate numeric fields
                            if field in ['contact_number', 'emergency_contact']:
                                try:
                                    int(new_value)
                                except ValueError:
                                    print(f"{label} must be numeric!")
                                    continue
                            cursor.execute(f"UPDATE students SET {field} = %s WHERE user_id = %s", (new_value, user_id))
                            print(f"✓ {label} updated")

                elif user_info['role'] in ('teacher', 'principal', 'academic_coordinator', 'admission_department'):
                    # Teacher-specific fields
                    fields_to_edit = {
                        'highest_qualifications': 'Qualifications',
                        'teaching_subject': 'Subject/Specialization'
                    }

                    for field, label in fields_to_edit.items():
                        current_value = details.get(field, '')
                        new_value = input(f"{label} (current: {current_value}): ").strip()
                        if new_value and new_value != current_value:
                            cursor.execute(f"UPDATE teachers SET {field} = %s WHERE user_id = %s", (new_value, user_id))
                            print(f"✓ {label} updated")

            self.connection.commit()
            print("\n✓ User details updated successfully!")

        except ValueError:
            print("Invalid input!")
        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

    def database_maintenance(self):
        """Admin: Database maintenance and cleanup"""
        print("\n" + "="*50)
        print("        DATABASE MAINTENANCE")
        print("="*50)
        print("WARNING: These operations will permanently delete data!")
        print("1. Clear All Teachers (Keep Admin)")
        print("2. Clear All Students")
        print("3. Clear All Classes")
        print("4. Clear All Subjects")
        print("5. Clear All Timetables")
        print("6. Clear All Attendance Records")
        print("7. Clear All Assignments and Privileges")
        print("8. Clear EVERYTHING (Fresh Start)")
        print("9. Back to Main Menu")

        choice = input("\nEnter choice (1-9): ").strip()

        if choice == '9':
            return

        # Confirmation
        confirm = input("\nAre you absolutely sure? This cannot be undone! (type 'YES' to confirm): ").strip()
        if confirm != 'YES':
            print("Operation cancelled.")
            return

        cursor = self.connection.cursor()

        try:
            if choice == '1':
                # Clear all teachers but keep admin
                cursor.execute("DELETE FROM teacher_privileges")
                cursor.execute("DELETE FROM teacher_assignments")
                cursor.execute("DELETE FROM teaching_records")
                cursor.execute("DELETE FROM teacher_attendance")
                cursor.execute("DELETE ta FROM timetable ta JOIN subjects s ON ta.subject_id = s.id WHERE s.teacher_id IS NOT NULL")
                cursor.execute("UPDATE subjects SET teacher_id = NULL")
                cursor.execute("DELETE FROM teachers")
                cursor.execute("DELETE FROM users WHERE role = 'teacher'")
                print("All teachers cleared successfully!")

            elif choice == '2':
                # Clear all students
                cursor.execute("DELETE FROM student_status")
                cursor.execute("DELETE FROM student_subjects")
                cursor.execute("DELETE FROM student_attendance")
                cursor.execute("DELETE FROM students")
                cursor.execute("DELETE FROM users WHERE role = 'student'")
                print("All students cleared successfully!")

            elif choice == '3':
                # Clear all classes
                cursor.execute("DELETE FROM teacher_assignments")
                cursor.execute("DELETE FROM student_subjects")
                cursor.execute("DELETE FROM subjects")
                cursor.execute("DELETE FROM timetable")
                cursor.execute("DELETE FROM classes")
                print("All classes cleared successfully!")

            elif choice == '4':
                # Clear all subjects
                cursor.execute("DELETE FROM student_subjects")
                cursor.execute("DELETE FROM teacher_assignments")
                cursor.execute("DELETE FROM timetable")
                cursor.execute("DELETE FROM subjects")
                print("All subjects cleared successfully!")

            elif choice == '5':
                # Clear all timetables
                cursor.execute("DELETE FROM timetable")
                print("All timetables cleared successfully!")

            elif choice == '6':
                # Clear all attendance records
                cursor.execute("DELETE FROM student_attendance")
                cursor.execute("DELETE FROM teacher_attendance")
                print("All attendance records cleared successfully!")

            elif choice == '7':
                # Clear all assignments and privileges
                cursor.execute("DELETE FROM teacher_privileges")
                cursor.execute("DELETE FROM teacher_assignments")
                print("All assignments and privileges cleared successfully!")

            elif choice == '8':
                # Clear EVERYTHING (Fresh Start)
                cursor.execute("DELETE FROM teacher_privileges")
                cursor.execute("DELETE FROM teacher_assignments")
                cursor.execute("DELETE FROM student_status")
                cursor.execute("DELETE FROM student_subjects")
                cursor.execute("DELETE FROM teaching_records")
                cursor.execute("DELETE FROM timetable")
                cursor.execute("DELETE FROM student_attendance")
                cursor.execute("DELETE FROM teacher_attendance")
                cursor.execute("DELETE FROM subjects")
                cursor.execute("DELETE FROM students")
                cursor.execute("DELETE FROM teachers")
                cursor.execute("DELETE FROM classes")
                cursor.execute("DELETE FROM users WHERE role != 'admin'")
                print("Complete database reset! Only admin remains.")
                print("Note: Default admin credentials - Username: admin, Password: admin123")

            else:
                print("Invalid choice!")
                cursor.close()
                return

            self.connection.commit()
            print("Database maintenance completed successfully!")

        except pymysql.Error as err:
            print(f"Database error: {err}")
            self.connection.rollback()
        finally:
            cursor.close()

def main():
    """
    Application entry point and exception handler.

    Instantiates the SchoolManagementSystem class and initiates the main program loop.
    Provides top-level exception handling for graceful error recovery and user feedback.

    Exception Handling:
        - KeyboardInterrupt: Handles user-initiated program interruption
        - Exception: Catches unexpected errors and displays diagnostic information

    Note:
        Ensures proper cleanup and user notification for all exit scenarios.
        MySQL configuration issues are reported with helpful guidance.
    """
    try:
        system = SchoolManagementSystem()
        system.run()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        print("Please check your MySQL configuration and try again.")

if __name__ == "__main__":
    main()
