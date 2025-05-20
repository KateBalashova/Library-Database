-- /The schema is fully normalized to 3NF:
-- 1NF: All tables have primary keys, and all attributes have atomic values.
-- 2NF: All non-key attributes are dependent on the entire primary key. For junction tables like book_author and book_genre, I made both foreign keys part of the composite primary key.
-- 3NF: I eliminated transitive dependencies by moving dependent attributes to their own entities:
-- Author information is in a separate table (not embedded in Book)
-- Genre information is separate from Book
-- Physical copy details are separate from Book metadata
-- Fee information is in its own table/

-- Create database
CREATE DATABASE library_management_system;
USE library_management_system;

-- Branch table
CREATE TABLE branch (
    branch_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(100) NOT NULL,
    opening_hours TIME NOT NULL,
    closing_hours TIME NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_branch_name UNIQUE (name),
    CONSTRAINT uq_branch_email UNIQUE (email)
);

-- Staff table
-- /Staff Hierarchy: a self-referential relationship in the
-- Staff table to represent manager-employee relationships./
CREATE TABLE staff (
    staff_id INT AUTO_INCREMENT PRIMARY KEY,
    branch_id INT NOT NULL,
    manager_id INT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    role ENUM('LIBRARIAN', 'MANAGER', 'ADMIN', 'ASSISTANT') NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    hire_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_staff_branch FOREIGN KEY (branch_id) REFERENCES branch(branch_id) ON DELETE RESTRICT,
    CONSTRAINT fk_staff_manager FOREIGN KEY (manager_id) REFERENCES staff(staff_id) ON DELETE SET NULL,
    CONSTRAINT uq_staff_email UNIQUE (email)
);

-- Patron table
CREATE TABLE patron (
    patron_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    registration_date DATE NOT NULL,
    membership_expiry DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    max_books_allowed INT DEFAULT 5,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_patron_email UNIQUE (email),
    CONSTRAINT chk_max_books_allowed CHECK (max_books_allowed > 0)
);

-- Genre table
CREATE TABLE genre (
    genre_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    description VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_genre_name UNIQUE (name)
);

-- Author table
CREATE TABLE author (
    author_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    birth_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_author_name UNIQUE (first_name, last_name, birth_date)
);

-- Book table (metadata)
-- // Separated Book and Book_Item entities:
-- Book contains metadata shared across all copies of a book
-- Book_Item contains instance-specific data like location and status//
CREATE TABLE book (
    book_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    isbn VARCHAR(20) NOT NULL,
    publication_year INT,
    language VARCHAR(50) DEFAULT 'English',
    num_pages INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT uq_book_isbn UNIQUE (isbn),
    CONSTRAINT chk_publication_year CHECK (publication_year IS NULL OR publication_year > 0),
    CONSTRAINT chk_num_pages CHECK (num_pages IS NULL OR num_pages > 0)
);

-- Book-Author junction table
CREATE TABLE book_author (
    book_id INT NOT NULL,
    author_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (book_id, author_id),
    CONSTRAINT fk_book_author_book FOREIGN KEY (book_id) REFERENCES book(book_id) ON DELETE CASCADE,
    CONSTRAINT fk_book_author_author FOREIGN KEY (author_id) REFERENCES author(author_id) ON DELETE CASCADE
);

-- Book-Genre junction table
CREATE TABLE book_genre (
    book_id INT NOT NULL,
    genre_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (book_id, genre_id),
    CONSTRAINT fk_book_genre_book FOREIGN KEY (book_id) REFERENCES book(book_id) ON DELETE CASCADE,
    CONSTRAINT fk_book_genre_genre FOREIGN KEY (genre_id) REFERENCES genre(genre_id) ON DELETE CASCADE
);

-- Book Item table (physical copies)
CREATE TABLE book_item (
    book_item_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    branch_id INT NOT NULL,
    barcode VARCHAR(50) NOT NULL,
    status ENUM('AVAILABLE', 'CHECKED_OUT', 'RESERVED', 'LOST', 'DAMAGED', 'BEING_REPAIRED') NOT NULL DEFAULT 'AVAILABLE',
    shelf_location VARCHAR(50) NOT NULL,
    acquisition_date DATE NOT NULL,
    price DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_book_item_book FOREIGN KEY (book_id) REFERENCES book(book_id) ON DELETE RESTRICT,
    CONSTRAINT fk_book_item_branch FOREIGN KEY (branch_id) REFERENCES branch(branch_id) ON DELETE RESTRICT,
    CONSTRAINT uq_book_item_barcode UNIQUE (barcode),
    CONSTRAINT chk_price CHECK (price IS NULL OR price >= 0)
);

-- Loan table
-- //Split checkout and return staff in Loan:
-- Different staff members may handle checkout vs. return//
CREATE TABLE loan (
    loan_id INT AUTO_INCREMENT PRIMARY KEY,
    book_item_id INT NOT NULL,
    patron_id INT NOT NULL,
    issuing_staff_id INT NOT NULL,
    returning_staff_id INT,
    checkout_date DATETIME NOT NULL,
    due_date DATE NOT NULL,
    return_date DATETIME,
    status ENUM('CURRENT', 'RETURNED', 'OVERDUE', 'LOST') DEFAULT 'CURRENT',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_loan_book_item FOREIGN KEY (book_item_id) REFERENCES book_item(book_item_id) ON DELETE RESTRICT,
    CONSTRAINT fk_loan_patron FOREIGN KEY (patron_id) REFERENCES patron(patron_id) ON DELETE RESTRICT,
    CONSTRAINT fk_loan_issuing_staff FOREIGN KEY (issuing_staff_id) REFERENCES staff(staff_id) ON DELETE RESTRICT,
    CONSTRAINT fk_loan_returning_staff FOREIGN KEY (returning_staff_id) REFERENCES staff(staff_id) ON DELETE RESTRICT,
    CONSTRAINT chk_loan_dates CHECK (return_date IS NULL OR return_date >= checkout_date)
);

-- Fine table
CREATE TABLE fine (
    fine_id INT AUTO_INCREMENT PRIMARY KEY,
    loan_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    issue_date DATETIME NOT NULL,
    payment_status ENUM('PENDING', 'PAID', 'WAIVED') DEFAULT 'PENDING',
    payment_date DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_fine_loan FOREIGN KEY (loan_id) REFERENCES loan(loan_id) ON DELETE RESTRICT,
    CONSTRAINT chk_fine_amount CHECK (amount > 0),
    CONSTRAINT chk_fine_dates CHECK (payment_date IS NULL OR payment_date >= issue_date)
);

-- Reservation table
CREATE TABLE reservation (
    reservation_id INT AUTO_INCREMENT PRIMARY KEY,
    book_id INT NOT NULL,
    patron_id INT NOT NULL,
    reservation_date DATETIME NOT NULL,
    expiry_date DATE NOT NULL,
    status ENUM('PENDING', 'FULFILLED', 'CANCELLED', 'EXPIRED') DEFAULT 'PENDING',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_reservation_book FOREIGN KEY (book_id) REFERENCES book(book_id) ON DELETE RESTRICT,
    CONSTRAINT fk_reservation_patron FOREIGN KEY (patron_id) REFERENCES patron(patron_id) ON DELETE RESTRICT,
    CONSTRAINT chk_reservation_dates CHECK (expiry_date >= DATE(reservation_date))
);

-- Create indexes for frequently queried fields
CREATE INDEX idx_book_title ON book(title);
CREATE INDEX idx_book_item_status ON book_item(status);
CREATE INDEX idx_patron_name ON patron(last_name, first_name);
CREATE INDEX idx_loan_dates ON loan(checkout_date, due_date, return_date);
CREATE INDEX idx_loan_status ON loan(status);
CREATE INDEX idx_fine_payment_status ON fine(payment_status);

-- Create view for available books
CREATE VIEW vw_available_books AS
SELECT
    b.book_id,
    b.title,
    b.isbn,
    GROUP_CONCAT(DISTINCT CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ') AS authors,
    GROUP_CONCAT(DISTINCT g.name SEPARATOR ', ') AS genres,
    COUNT(bi.book_item_id) AS available_copies,
    br.name AS branch_name
FROM
    book b
JOIN
    book_item bi ON b.book_id = bi.book_id
JOIN
    branch br ON bi.branch_id = br.branch_id
LEFT JOIN
    book_author ba ON b.book_id = ba.book_id
LEFT JOIN
    author a ON ba.author_id = a.author_id
LEFT JOIN
    book_genre bg ON b.book_id = bg.book_id
LEFT JOIN
    genre g ON bg.genre_id = g.genre_id
WHERE
    bi.status = 'AVAILABLE'
GROUP BY
    b.book_id, br.branch_id;

-- Create view for patron loans
CREATE VIEW vw_patron_loans AS
SELECT
    p.patron_id,
    CONCAT(p.first_name, ' ', p.last_name) AS patron_name,
    b.title AS book_title,
    l.checkout_date,
    l.due_date,
    l.return_date,
    l.status AS loan_status,
    IFNULL(f.amount, 0) AS fine_amount,
    f.payment_status
FROM
    patron p
JOIN
    loan l ON p.patron_id = l.patron_id
JOIN
    book_item bi ON l.book_item_id = bi.book_item_id
JOIN
    book b ON bi.book_id = b.book_id
LEFT JOIN
    fine f ON l.loan_id = f.loan_id;

-- Create a stored procedure for checking out books
DELIMITER //
CREATE PROCEDURE sp_checkout_book(
    IN p_book_item_id INT,
    IN p_patron_id INT,
    IN p_staff_id INT,
    IN p_due_days INT
)
BEGIN
    DECLARE v_book_status VARCHAR(20);
    DECLARE v_patron_active BOOLEAN;
    DECLARE v_current_loans INT;
    DECLARE v_max_allowed INT;

    -- Check if book is available
    SELECT status INTO v_book_status FROM book_item WHERE book_item_id = p_book_item_id;
    IF v_book_status != 'AVAILABLE' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Book is not available for checkout';
    END IF;

    -- Check if patron is active
    SELECT is_active, max_books_allowed INTO v_patron_active, v_max_allowed
    FROM patron WHERE patron_id = p_patron_id;
    IF v_patron_active != TRUE THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Patron account is not active';
    END IF;

    -- Check if patron has reached max books limit
    SELECT COUNT(*) INTO v_current_loans
    FROM loan
    WHERE patron_id = p_patron_id AND status IN ('CURRENT', 'OVERDUE');
    IF v_current_loans >= v_max_allowed THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Patron has reached maximum allowed books';
    END IF;

    -- Process checkout
    START TRANSACTION;

    -- Update book status
    UPDATE book_item SET status = 'CHECKED_OUT' WHERE book_item_id = p_book_item_id;

    -- Create loan record
    INSERT INTO loan (
        book_item_id,
        patron_id,
        issuing_staff_id,
        checkout_date,
        due_date,
        status
    ) VALUES (
        p_book_item_id,
        p_patron_id,
        p_staff_id,
        NOW(),
        DATE_ADD(CURRENT_DATE(), INTERVAL p_due_days DAY),
        'CURRENT'
    );

    COMMIT;
END //
DELIMITER ;

-- Create a stored procedure for returning books
DELIMITER //
CREATE PROCEDURE sp_return_book(
    IN p_book_item_id INT,
    IN p_staff_id INT,
    OUT p_fine_amount DECIMAL(10,2)
)
BEGIN
    DECLARE v_loan_id INT;
    DECLARE v_due_date DATE;
    DECLARE v_days_overdue INT;
    DECLARE v_fine_rate DECIMAL(10, 2) DEFAULT 0.50; -- $0.50 per day

    SET p_fine_amount = 0;

    -- Find the loan
    SELECT loan_id, due_date INTO v_loan_id, v_due_date
    FROM loan
    WHERE book_item_id = p_book_item_id AND return_date IS NULL
    ORDER BY checkout_date DESC LIMIT 1;

    IF v_loan_id IS NULL THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No active loan found for this book';
    END IF;

    START TRANSACTION;

    -- Update book status
    UPDATE book_item SET status = 'AVAILABLE' WHERE book_item_id = p_book_item_id;

    -- Update loan record
    UPDATE loan SET
        return_date = NOW(),
        returning_staff_id = p_staff_id,
        status = 'RETURNED'
    WHERE loan_id = v_loan_id;

    -- Calculate and create fine if overdue
    IF v_due_date < CURRENT_DATE() THEN
        SET v_days_overdue = DATEDIFF(CURRENT_DATE(), v_due_date);
        SET p_fine_amount = v_days_overdue * v_fine_rate;

        INSERT INTO fine (
            loan_id,
            amount,
            issue_date,
            payment_status
        ) VALUES (
            v_loan_id,
            p_fine_amount,
            NOW(),
            'PENDING'
        );
    END IF;

    COMMIT;
END //
DELIMITER ;

-- Create trigger to update book status when reservation is fulfilled
DELIMITER //
CREATE TRIGGER trg_update_book_status_after_reservation
AFTER UPDATE ON reservation
FOR EACH ROW
BEGIN
    DECLARE v_book_item_id INT;

    IF NEW.status = 'FULFILLED' AND OLD.status != 'FULFILLED' THEN
        -- Find an available copy of the book at any branch
        SELECT book_item_id INTO v_book_item_id
        FROM book_item
        WHERE book_id = NEW.book_id AND status = 'AVAILABLE'
        LIMIT 1;

        IF v_book_item_id IS NOT NULL THEN
            -- Update the book status to reserved
            UPDATE book_item
            SET status = 'RESERVED'
            WHERE book_item_id = v_book_item_id;
        END IF;
    END IF;
END //
DELIMITER ;

-- Create trigger to update loan status when overdue
DELIMITER //
CREATE TRIGGER trg_update_loan_status_daily
BEFORE UPDATE ON loan
FOR EACH ROW
BEGIN
    -- Check if loan is overdue
    IF NEW.status = 'CURRENT' AND NEW.due_date < CURRENT_DATE() THEN
        SET NEW.status = 'OVERDUE';
    END IF;
END //
DELIMITER ;