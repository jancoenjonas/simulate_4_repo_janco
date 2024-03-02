CREATE DATABASE IF NOT EXISTS flask_local_database_test;
USE flask_local_database_test;

-- Drop tables if they exist to prevent errors
DROP TABLE IF EXISTS student_lessons;
DROP TABLE IF EXISTS nfc_tags;
DROP TABLE IF EXISTS streaks;
DROP TABLE IF EXISTS lessons;
DROP TABLE IF EXISTS users;

-- Creation of users table with UUID
CREATE TABLE users (
    id CHAR(36) NOT NULL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('STUDENT', 'TEACHER') NOT NULL,
    major VARCHAR(255)
);

-- Creation of lessons table with UUID
CREATE TABLE lessons (
    id CHAR(36) NOT NULL PRIMARY KEY,
    teacher_id CHAR(36) NOT NULL,
    time VARCHAR(5) NOT NULL,
    name VARCHAR(255) NOT NULL,
    attendance ENUM('ATTENDED', 'LATE', 'ABSENT', 'UPCOMING') NOT NULL,
    day VARCHAR(9) NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);

-- Creation of streaks table with UUID
CREATE TABLE streaks (
    id CHAR(36) NOT NULL PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    current_streak INT DEFAULT 0,
    longest_streak INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Creation of nfc_tags table with UUID
CREATE TABLE nfc_tags (
    id CHAR(36) NOT NULL PRIMARY KEY,
    tag_data VARCHAR(255) NOT NULL UNIQUE,
    scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_id CHAR(36),
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Creation of student_lessons junction table with UUID
CREATE TABLE student_lessons (
    student_id CHAR(36) NOT NULL,
    lesson_id CHAR(36) NOT NULL,
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (lesson_id) REFERENCES lessons(id),
    PRIMARY KEY (student_id, lesson_id)
);


