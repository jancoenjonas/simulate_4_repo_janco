-- Kies de database
create database flask_local_database_test_2;

use flask_local_database_test_2;

-- Gebruikers tabel
CREATE TABLE IF NOT EXISTS users (
    id CHAR(36) NOT NULL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('STUDENT', 'TEACHER') NOT NULL,
    major VARCHAR(255)
);

-- Lessen tabel
CREATE TABLE IF NOT EXISTS lessons (
    id CHAR(36) NOT NULL PRIMARY KEY,
    teacher_id CHAR(36) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    date DATE NOT NULL,
    name VARCHAR(255) NOT NULL,
    status ENUM('ACTIVE', 'CANCELLED') NOT NULL DEFAULT 'ACTIVE',
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);

-- Aanwezigheid tabel
CREATE TABLE IF NOT EXISTS lesson_attendance (
    id CHAR(36) NOT NULL PRIMARY KEY,
    lesson_id CHAR(36) NOT NULL,
    student_id CHAR(36) NOT NULL,
    attendance_status ENUM('ATTENDED', 'LATE', 'ABSENT') NOT NULL,
    attendance_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lesson_id) REFERENCES lessons(id),
    FOREIGN KEY (student_id) REFERENCES users(id)
);

-- NFC Tags tabel
CREATE TABLE IF NOT EXISTS nfc_tags (
    id CHAR(36) NOT NULL PRIMARY KEY,
    tag_data VARCHAR(255) NOT NULL UNIQUE,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id CHAR(36),
    lesson_id CHAR(36),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id)
);

-- Student-Les koppelingstabel
CREATE TABLE IF NOT EXISTS student_lessons (
    student_id CHAR(36) NOT NULL,
    lesson_id CHAR(36) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id),
    PRIMARY KEY (student_id, lesson_id)
);

-- Vooraf bepaalde UUIDs
SET @teacherUUID := '123e4567-e89b-12d3-a456-426614174000';
SET @studentUUID := '76e2f721-e9aa-4ba2-af8e-3563fd280b01';

-- Gebruikers
INSERT INTO users (id, username, password, role, major) VALUES
(@teacherUUID, 'teacher1', 'password', 'TEACHER', 'Informatica'),
(@studentUUID, 'student1', 'password', 'STUDENT', 'Informatica');

-- Lessen (gebruik de vooraf bepaalde @teacherUUID)
-- Een les in het verleden
INSERT INTO lessons (id, teacher_id, start_time, end_time, date, name, status) VALUES
(UUID(), @teacherUUID, '09:00:00', '11:00:00', CURDATE() - INTERVAL 1 DAY, 'Wiskunde', 'ACTIVE');

-- Een les vandaag
INSERT INTO lessons (id, teacher_id, start_time, end_time, date, name, status) VALUES
(UUID(), @teacherUUID, '10:00:00', '12:00:00', CURDATE(), 'Programmeren 101', 'ACTIVE');

-- Een les in de toekomst
INSERT INTO lessons (id, teacher_id, start_time, end_time, date, name, status) VALUES
(UUID(), @teacherUUID, '13:00:00', '15:00:00', CURDATE() + INTERVAL 1 DAY, 'Geschiedenis', 'ACTIVE');