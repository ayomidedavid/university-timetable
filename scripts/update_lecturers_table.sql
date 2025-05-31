ALTER TABLE lecturers
ADD COLUMN title ENUM('Mr', 'Mrs', 'Ms', 'Dr', 'Prof') NOT NULL DEFAULT 'Mr';