-- Drop tables if they exist to prevent errors
DROP TABLE IF EXISTS nfc_tags;
DROP TABLE IF EXISTS streaks;
DROP TABLE IF EXISTS lessons;
DROP TABLE IF EXISTS users;

-- Creation of users table
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('STUDENT', 'TEACHER') NOT NULL,
    major VARCHAR(255)
);

-- Creation of lessons table
CREATE TABLE lessons (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    time VARCHAR(5) NOT NULL,
    name VARCHAR(255) NOT NULL,
    attendance ENUM('ATTENDED', 'LATE', 'ABSENT', 'UPCOMING') NOT NULL,
    day VARCHAR(9) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Creation of streaks table
CREATE TABLE streaks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    current_streak INT DEFAULT 0,
    longest_streak INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Creation of nfc_tags table
CREATE TABLE nfc_tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tag_data VARCHAR(255) NOT NULL UNIQUE,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Inserting sample users
INSERT INTO users (username, password, role, major) VALUES
('janco', 'itPass', 'STUDENT', 'IT'),
('lisa', 'itPass123', 'STUDENT', 'IT'),
('bob', 'itTeacherPass', 'TEACHER', 'IT'),
('steven', 'philosophyTeacherPass', 'TEACHER', 'Philosophy'),
('tim', 'aiTeacherPass', 'TEACHER', 'AI');

-- Inserting sample lessons
-- (You'll need to replace user_id with the actual IDs from the users table)
INSERT INTO lessons (user_id, time, name, attendance, day) VALUES
(1, '08:00', 'Software Development', 'ATTENDED', 'Monday'),
(1, '10:00', 'Network Security', 'UPCOMING', 'Monday'),
(2, '08:00', 'Software Development', 'UPCOMING', 'Monday'),
(2, '10:00', 'Data Structures', 'UPCOMING', 'Monday');

-- Inserting sample streaks
INSERT INTO streaks (user_id, current_streak, longest_streak) VALUES
(1, 10, 15),
(2, 7, 12);

-- Inserting sample NFC tag data
-- (You'll need to replace user_id with the actual IDs from the users table)
INSERT INTO nfc_tags (tag_data, user_id) VALUES
('04:A7:83:AE', 1),
('04:B6:22:AF', 2);
