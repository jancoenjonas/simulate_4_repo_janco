use jancotest;
-- Assuming the users table is already created and populated

-- Redefine the lessons table to include new fields
DROP TABLE IF EXISTS lessons;

CREATE TABLE lessons (
    id CHAR(36) NOT NULL PRIMARY KEY,
    teacher_id CHAR(36) NOT NULL,
    title VARCHAR(255) NOT NULL,
    start TIME NOT NULL,
    end TIME NOT NULL,
    dow INT NOT NULL,
    color VARCHAR(7) NOT NULL,
    type VARCHAR(50) NOT NULL,
    subgroep VARCHAR(50) NOT NULL,
    campus VARCHAR(50) NOT NULL,
    lokaal VARCHAR(50) NOT NULL,
    FOREIGN KEY (teacher_id) REFERENCES users(id)
);
