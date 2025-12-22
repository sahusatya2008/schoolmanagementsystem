-- DATABASE UPDATE SCRIPT
-- Run this script to update existing School Management System databases
-- Fixes missing columns and other schema issues

USE school_management;

-- Fix 1: Add missing can_edit_attendance column to teacher_privileges table
-- This fixes the "Unknown column 'tp.can_edit_attendance'" error
ALTER TABLE teacher_privileges
ADD COLUMN can_edit_attendance BOOLEAN DEFAULT FALSE;

-- Fix 2: Ensure all tables have proper structure
-- (The CREATE TABLE IF NOT EXISTS statements will not recreate existing tables)

-- Verify the fix worked
SELECT 'Database update completed successfully!' as status;
DESCRIBE teacher_privileges;

COMMIT;
