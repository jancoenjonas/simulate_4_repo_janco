CREATE TABLE EventDate (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL
);

CREATE TABLE EventTimeSlot (
    id INT AUTO_INCREMENT PRIMARY KEY,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);

CREATE TABLE EventLocation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    room VARCHAR(100) NOT NULL
);

CREATE TABLE EventActivityType (
    id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(50) NOT NULL
);

CREATE TABLE EventInstructor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE EventActivity (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    date_id INT,
    timeslot_id INT,
    location_id INT,
    type_id INT,
    FOREIGN KEY (date_id) REFERENCES EventDate(id),
    FOREIGN KEY (timeslot_id) REFERENCES EventTimeSlot(id),
    FOREIGN KEY (location_id) REFERENCES EventLocation(id),
    FOREIGN KEY (type_id) REFERENCES EventActivityType(id)
);

CREATE TABLE EventActivityInstructor (
    activity_id INT,
    instructor_id INT,
    PRIMARY KEY (activity_id, instructor_id),
    FOREIGN KEY (activity_id) REFERENCES EventActivity(id),
    FOREIGN KEY (instructor_id) REFERENCES EventInstructor(id)
);
