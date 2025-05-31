CREATE DATABASE university_db;
USE university_db;

-- HOD Table
CREATE TABLE IF NOT EXISTS hod (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL
);


-- Faculty Table
CREATE TABLE faculty (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_name VARCHAR(255) UNIQUE NOT NULL,
    faculty_description TEXT
);

-- Department Table
CREATE TABLE department (
    department_id INT AUTO_INCREMENT PRIMARY KEY,
    department_name VARCHAR(255) UNIQUE NOT NULL,
    hod_id INT,
    faculty_id INT,
    FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
);

-- HOD Table
CREATE TABLE hod (
    hod_id INT AUTO_INCREMENT PRIMARY KEY,
    hod_name VARCHAR(255) NOT NULL,
    department_id INT UNIQUE,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

-- Lecturers Table
CREATE TABLE lecturers (
    lecture_id INT AUTO_INCREMENT PRIMARY KEY,
    lecture_firstname VARCHAR(255) NOT NULL,
    lecture_lastname VARCHAR(255) NOT NULL,
    lecture_middlename VARCHAR(255),
    department_id INT,
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

-- Courses Table
CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(255) NOT NULL,
    course_code VARCHAR(50) UNIQUE NOT NULL,
    course_unit INT NOT NULL,
    num_of_students INT DEFAULT 0,
    lecture_id INT,
    department_id INT,
    level INT NOT NULL,
    FOREIGN KEY (lecture_id) REFERENCES lecturers(lecture_id),
    FOREIGN KEY (department_id) REFERENCES department(department_id)
);

-- Venue Table
CREATE TABLE venue (
    venue_id INT AUTO_INCREMENT PRIMARY KEY,
    venue_name VARCHAR(255) UNIQUE NOT NULL,
    venue_size INT NOT NULL,
    venue_location VARCHAR(255) NOT NULL
);

-- Timetable Table (Transaction Table for Scheduling)
CREATE TABLE timetable (
    id INT AUTO_INCREMENT PRIMARY KEY,
    day VARCHAR(20),
    time_slot VARCHAR(50),
    course_name VARCHAR(100),
    venue VARCHAR(100),
    lecturer VARCHAR(100)
);

-- Admin Table
CREATE TABLE admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Unit Table
CREATE TABLE unit_table (
    unit_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT,
    unit_hours INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

INSERT INTO admin (username, password_hash)
VALUES ('admin', SHA2('admin123', 256));

