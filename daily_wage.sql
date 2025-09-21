INSERT INTO worker (name, wage) VALUES ("Ram", 900);
SELECT * FROM worker;
INSERT INTO worker (name, wage,occupation,contact) VALUES ("Rani", 300, "maid", 9876899899);
SHOW TABLES;
SELECT * FROM user;
DESCRIBE user;
ALTER TABLE user MODIFY COLUMN password VARCHAR(500);

CREATE TABLE workers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    wage INT NOT NULL
);ALTER TABLE worker ADD COLUMN occupation VARCHAR(100) NOT NULL;
ALTER TABLE worker ADD COLUMN contact VARCHAR(15) NOT NULL;
ALTER TABLE user ADD COLUMN contact VARCHAR(15) NOT NULL;
ALTER TABLE user ADD COLUMN fullname VARCHAR(15) NOT NULL;
DESCRIBE worker;
TRUNCATE TABLE worker;
TRUNCATE TABLE user;
ALTER TABLE worker
ADD COLUMN working_hours VARCHAR(20) NOT NULL,
ADD COLUMN location VARCHAR(100) NOT NULL;

USE daily_wage_db;

-- Rename 'user' table to 'accounts' (or any name you prefer)
ALTER TABLE user RENAME TO accounts;

-- Make sure role exists
ALTER TABLE accounts
ADD COLUMN role ENUM('user', 'worker') NOT NULL DEFAULT 'user';

-- Ensure contact and fullname exist
ALTER TABLE accounts
ADD COLUMN contact VARCHAR(15) NOT NULL,
ADD COLUMN fullname VARCHAR(50) NOT NULL;

-- Make password length bigger if needed
ALTER TABLE accounts MODIFY COLUMN password VARCHAR(500);





