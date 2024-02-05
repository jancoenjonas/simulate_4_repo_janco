-- Database aanmaken genaamd 'attendance_tracker'
CREATE DATABASE attendance_tracker;

-- Gebruik de aangemaakte database
USE attendance_tracker;

-- Aanmaken van de 'students' tabel om studentengegevens op te slaan
CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    card_uid VARCHAR(100) NOT NULL UNIQUE -- NFC card unieke identifier
);

-- Aanmaken van de 'classes' tabel om lesinformatie op te slaan
CREATE TABLE classes (
    class_id INT AUTO_INCREMENT PRIMARY KEY,
    class_name VARCHAR(100) NOT NULL,
    class_description TEXT
);

-- Aanmaken van de 'attendance' tabel om aanwezigheidsgegevens op te slaan
CREATE TABLE attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    attendance_time TIME NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (class_id) REFERENCES classes(class_id)
);
