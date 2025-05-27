USE library_management_system;

SET SQL_SAFE_UPDATES = 0;
SET FOREIGN_KEY_CHECKS = 0;

DELETE FROM fine;
DELETE FROM loan;
DELETE FROM reservation;
DELETE FROM book_item;
DELETE FROM book_author;
DELETE FROM book_genre;
DELETE FROM book;
DELETE FROM author;
DELETE FROM genre;
DELETE FROM patron;
DELETE FROM staff;
DELETE FROM branch;

ALTER TABLE branch AUTO_INCREMENT = 1;
ALTER TABLE staff AUTO_INCREMENT = 1;
ALTER TABLE patron AUTO_INCREMENT = 1;
ALTER TABLE genre AUTO_INCREMENT = 1;
ALTER TABLE author AUTO_INCREMENT = 1;
ALTER TABLE book AUTO_INCREMENT = 1;
ALTER TABLE book_item AUTO_INCREMENT = 1;
ALTER TABLE loan AUTO_INCREMENT = 1;
ALTER TABLE fine AUTO_INCREMENT = 1;
ALTER TABLE reservation AUTO_INCREMENT = 1;

SET FOREIGN_KEY_CHECKS = 1;

-- Ensure AUTO_INCREMENT is enabled
ALTER TABLE branch MODIFY COLUMN branch_id INT AUTO_INCREMENT;
ALTER TABLE staff MODIFY COLUMN staff_id INT AUTO_INCREMENT;
ALTER TABLE patron MODIFY COLUMN patron_id INT AUTO_INCREMENT;
ALTER TABLE genre MODIFY COLUMN genre_id INT AUTO_INCREMENT;
ALTER TABLE author MODIFY COLUMN author_id INT AUTO_INCREMENT;
ALTER TABLE book MODIFY COLUMN book_id INT AUTO_INCREMENT;
ALTER TABLE book_item MODIFY COLUMN book_item_id INT AUTO_INCREMENT;
ALTER TABLE loan MODIFY COLUMN loan_id INT AUTO_INCREMENT;
ALTER TABLE fine MODIFY COLUMN fine_id INT AUTO_INCREMENT;
ALTER TABLE reservation MODIFY COLUMN reservation_id INT AUTO_INCREMENT;

-- Insert branch
INSERT INTO branch (name, address, phone, email, opening_hours, closing_hours)
VALUES ('Central Library', '123 Main St', '0123456789', 'central@library.com', '08:00:00', '18:00:00');
SET @branch_id = LAST_INSERT_ID();

-- Insert staff
INSERT INTO staff (branch_id, manager_id, first_name, last_name, email, phone, role, password_hash, hire_date, is_active)
VALUES 
(@branch_id, NULL, 'Alice', 'Admin', 'admin@library.com', '0123456789', 'ADMIN',
 '$2b$12$MvxSKZ6A2t/Hm8ik7STUXugIMYJLrjsoeWIQ9S8LlBkEGBy9z/qHi', CURDATE(), 1);
SET @staff_id = LAST_INSERT_ID();

-- Insert genres
INSERT INTO genre (name, description) VALUES 
('Fantasy', 'Fantasy books'),
('Sci-Fi', 'Science Fiction'),
('Mystery', 'Detective stories'),
('Romance', 'Love stories'),
('Non-Fiction', 'Factual content');

-- Insert authors
INSERT INTO author (first_name, last_name, birth_date) VALUES
('J.K.', 'Rowling', '1965-07-31'),
('George', 'Orwell', '1903-06-25'),
('Agatha', 'Christie', '1890-09-15'),
('Nicholas', 'Sparks', '1965-12-31'),
('Malcolm', 'Gladwell', '1963-09-03');

-- Insert books
INSERT INTO book (title, isbn, publication_year, language, num_pages) VALUES
('Harry Potter', '1111111111111', 1997, 'English', 320),
('1984', '2222222222222', 1949, 'English', 270),
('Murder on the Orient Express', '3333333333333', 1934, 'English', 280),
('The Notebook', '4444444444444', 1996, 'English', 250),
('Outliers', '5555555555555', 2008, 'English', 300);

-- Capture book IDs
SET @book1_id = LAST_INSERT_ID() ;
SET @book2_id = LAST_INSERT_ID() + 1;
SET @book3_id = LAST_INSERT_ID() + 2;
SET @book4_id = LAST_INSERT_ID() + 3;
SET @book5_id = LAST_INSERT_ID() + 4;

-- Map books to genres and authors
INSERT INTO book_author (book_id, author_id) VALUES
(@book1_id, 1), (@book2_id, 2), (@book3_id, 3), (@book4_id, 4), (@book5_id, 5);

INSERT INTO book_genre (book_id, genre_id) VALUES
(@book1_id, 1), (@book2_id, 2), (@book3_id, 3), (@book4_id, 4), (@book5_id, 5);

-- Book items
INSERT INTO book_item (book_id, branch_id, barcode, status, shelf_location, acquisition_date, price) VALUES
(@book1_id, @branch_id, 'BC101', 'AVAILABLE', 'A1', CURDATE(), 20.00),
(@book2_id, @branch_id, 'BC102', 'AVAILABLE', 'A1', CURDATE(), 18.00),
(@book3_id, @branch_id, 'BC103', 'AVAILABLE', 'A1', CURDATE(), 22.00),
(@book4_id, @branch_id, 'BC104', 'AVAILABLE', 'A1', CURDATE(), 19.00),
(@book5_id, @branch_id, 'BC105', 'AVAILABLE', 'A1', CURDATE(), 24.00);

SELECT book_item_id INTO @item1 FROM book_item WHERE barcode = 'BC101';
SELECT book_item_id INTO @item2 FROM book_item WHERE barcode = 'BC102';
SELECT book_item_id INTO @item3 FROM book_item WHERE barcode = 'BC103';
SELECT book_item_id INTO @item4 FROM book_item WHERE barcode = 'BC104';
SELECT book_item_id INTO @item5 FROM book_item WHERE barcode = 'BC105';


SELECT patron_id INTO @patron_id FROM patron WHERE email = 'test@123';

-- RETURNED Loans over 6 months
INSERT INTO loan (book_item_id, patron_id, issuing_staff_id, returning_staff_id, checkout_date, due_date, return_date, status) VALUES
(@item1, @patron_id, @staff_id, @staff_id, DATE_SUB(CURDATE(), INTERVAL 6 MONTH), DATE_SUB(CURDATE(), INTERVAL 5 MONTH), DATE_SUB(CURDATE(), INTERVAL 5 MONTH), 'RETURNED'),
(@item2, @patron_id, @staff_id, @staff_id, DATE_SUB(CURDATE(), INTERVAL 5 MONTH), DATE_SUB(CURDATE(), INTERVAL 4 MONTH), DATE_SUB(CURDATE(), INTERVAL 4 MONTH), 'RETURNED'),
(@item3, @patron_id, @staff_id, @staff_id, DATE_SUB(CURDATE(), INTERVAL 4 MONTH), DATE_SUB(CURDATE(), INTERVAL 3 MONTH), DATE_SUB(CURDATE(), INTERVAL 3 MONTH), 'RETURNED'),
(@item4, @patron_id, @staff_id, @staff_id, DATE_SUB(CURDATE(), INTERVAL 3 MONTH), DATE_SUB(CURDATE(), INTERVAL 2 MONTH), DATE_SUB(CURDATE(), INTERVAL 2 MONTH), 'RETURNED'),
(@item5, @patron_id, @staff_id, @staff_id, DATE_SUB(CURDATE(), INTERVAL 2 MONTH), DATE_SUB(CURDATE(), INTERVAL 1 MONTH), DATE_SUB(CURDATE(), INTERVAL 1 MONTH), 'RETURNED'),
(@item1, @patron_id, @staff_id, @staff_id, DATE_SUB(CURDATE(), INTERVAL 1 MONTH), CURDATE(), CURDATE(), 'RETURNED');

-- CURRENT Loans
INSERT INTO loan (book_item_id, patron_id, issuing_staff_id, checkout_date, due_date, status) VALUES
(@item2, @patron_id, @staff_id, DATE_SUB(CURDATE(), INTERVAL 15 DAY), DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'CURRENT'),
(@item3, @patron_id, @staff_id, DATE_SUB(CURDATE(), INTERVAL 5 DAY), DATE_ADD(CURDATE(), INTERVAL 15 DAY), 'CURRENT'),
(@item4, @patron_id, @staff_id, DATE_SUB(CURDATE(), INTERVAL 3 DAY), DATE_ADD(CURDATE(), INTERVAL 10 DAY), 'CURRENT');

-- OVERDUE Loans
INSERT INTO loan (book_item_id, patron_id, issuing_staff_id, checkout_date, due_date, status) VALUES
(@item5, @patron_id, @staff_id, DATE_SUB(CURDATE(), INTERVAL 30 DAY), DATE_SUB(CURDATE(), INTERVAL 10 DAY), 'OVERDUE'),
(@item1, @patron_id, @staff_id, DATE_SUB(CURDATE(), INTERVAL 20 DAY), DATE_SUB(CURDATE(), INTERVAL 5 DAY), 'OVERDUE'),
(@item2, @patron_id, @staff_id, DATE_SUB(CURDATE(), INTERVAL 25 DAY), DATE_SUB(CURDATE(), INTERVAL 2 DAY), 'OVERDUE');



-- Create the view
CREATE OR REPLACE VIEW vw_patron_loans AS
SELECT
  p.patron_id,
  CONCAT(p.first_name, ' ', p.last_name) AS patron_name,
  b.title AS book_title,
  GROUP_CONCAT(DISTINCT CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ') AS authors,
  GROUP_CONCAT(DISTINCT g.name SEPARATOR ', ') AS genres,
  l.checkout_date,
  l.due_date,
  l.return_date,
  l.status AS loan_status,
  IFNULL(f.amount, 0) AS fine_amount,
  f.payment_status
FROM
  loan l
JOIN book_item bi ON l.book_item_id = bi.book_item_id
JOIN book b ON bi.book_id = b.book_id
LEFT JOIN book_author ba ON b.book_id = ba.book_id
LEFT JOIN author a ON ba.author_id = a.author_id
LEFT JOIN book_genre bg ON b.book_id = bg.book_id
LEFT JOIN genre g ON bg.genre_id = g.genre_id
JOIN patron p ON l.patron_id = p.patron_id
LEFT JOIN fine f ON l.loan_id = f.loan_id
GROUP BY l.loan_id;


SET @branch_id = 1;

-- Create an admin staff (manager)
INSERT INTO staff (branch_id, first_name, last_name, email, phone, role, password_hash, hire_date)
VALUES (@branch_id, 'Alice', 'Admin', 'alice@library.com', '1234567890', 'ADMIN', 'hashedpass1', '2023-01-01');
-- Save manager_id
SET @manager_id = LAST_INSERT_ID();

-- Create a librarian under that manager
INSERT INTO staff (branch_id, manager_id, first_name, last_name, email, phone, role, password_hash, hire_date)
VALUES (@branch_id, @manager_id, 'TestStaff', 'Librarian', 'test@staff', '1234567891', 'LIBRARIAN', 'hashedpass2', '2023-02-01');
-- Save librarian_id
SET @librarian_id = LAST_INSERT_ID();

-- Add a patron
INSERT INTO patron (first_name, last_name, email, phone, registration_date, membership_expiry)
VALUES ('Charlie', 'Reader', 'charlie@domain.com', '1234567892', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 1 YEAR));
-- Save patron_id
SET @patron_id = LAST_INSERT_ID();

-- Add an author
INSERT INTO author (first_name, last_name, birth_date)
VALUES ('John', 'Doe', '1970-01-01');
-- Save author_id
SET @auth_id = LAST_INSERT_ID();

-- Add a genre
INSERT INTO genre (name, description)
VALUES ('Sci-Fi', 'Science fiction books with futuristic themes');
-- Save genre_id
SET @genre_id = LAST_INSERT_ID();

-- Add a book
INSERT INTO book (title, isbn, publication_year, language, num_pages)
VALUES ('Galactic Tales', '9781234567897', 2020, 'English', 350);
-- Save book_id
SET @book_id = LAST_INSERT_ID();

-- Link book to author and genre
INSERT INTO book_author (book_id, author_id) VALUES (@book_id, @auth_id);
INSERT INTO book_genre (book_id, genre_id) VALUES (@book_id, @genre_id);

-- Add a book item
INSERT INTO book_item (book_id, branch_id, barcode, status, shelf_location, acquisition_date, price)
VALUES (@book_id, @branch_id, 'BC1234567890', 'AVAILABLE', 'SHELF-A1', CURDATE(), 29.99);
-- Save book_item_id
SET @book_item_id = LAST_INSERT_ID();

-- Create a loan by patron processed by librarian
INSERT INTO loan (book_item_id, patron_id, issuing_staff_id, checkout_date, due_date, status)
VALUES (@book_item_id, @patron_id, @librarian_id, NOW(), DATE_ADD(CURDATE(), INTERVAL 14 DAY), 'CURRENT');
-- Save loan_id
SET @loan_id = LAST_INSERT_ID();

-- Add a fine for the loan
INSERT INTO fine (loan_id, amount, issue_date)
VALUES (@loan_id, 10.00, NOW());

-- Add a reservation
INSERT INTO reservation (book_id, patron_id, reservation_date, expiry_date)
VALUES (@book_id, @patron_id, NOW(), DATE_ADD(CURDATE(), INTERVAL 7 DAY));


