-- Create the database named 'attendance_tracker'
CREATE DATABASE IF NOT EXISTS attendance_tracker;

-- Use the created database
USE attendance_tracker;

-- Create the 'students' table to store student data
CREATE TABLE students (
    student_id CHAR(36) PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    card_uid VARCHAR(100) NOT NULL UNIQUE -- NFC card unique identifier
);

-- Create the 'classes' table to store class information
CREATE TABLE classes (
    class_id CHAR(36) PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    class_description TEXT
);

-- Create the 'attendance' table to store attendance data
CREATE TABLE attendance (
    attendance_id CHAR(36) PRIMARY KEY,
    student_id CHAR(36) NOT NULL,
    class_id CHAR(36) NOT NULL,
    attendance_date DATE NOT NULL,
    attendance_time TIME NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
);

-- Create the 'streaks' table to store streak data for each student
CREATE TABLE streaks (
    streak_id CHAR(36) PRIMARY KEY,
    student_id CHAR(36) NOT NULL,
    current_streak INT NOT NULL DEFAULT 0,
    longest_streak INT NOT NULL DEFAULT 0,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);
