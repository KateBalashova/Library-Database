# 📚 Library Management System
---

## 📄 Project Description

This project aims to design a system that would allow for convenient and secure management of a system of libraries. Planned capabilities include managing patron information, book loans, staff permissions, and more.

---

## 🎯 Functional & Non-functional Requirements

### Functional Requirements

1.  User Management
-   Register and manage library patrons with essential contact details
-   Track membership status and send expiry notifications
-   Allow patrons to view their borrowing history and current loans
    
2.  Book Management
-   Maintain catalog with key book metadata (title, author, ISBN, genre)
-   Track book status (available, checked out, lost, damaged)
-   Support basic search functionality by title, author, and genre

3.  Circulation Management
-   Process book checkouts and returns with staff authorization
-   Calculate late fees based on configurable rules
-   Enforce borrowing limits and loan durations per patron
    
4.  Branch Management
-   Store information about multiple library locations across the city
-   Associate books and staff with specific branches
-   Support book transfers between branches when requested

5.  Staff Management
-   Maintain staff records with role-based permissions
-   Track which staff member processes each transaction for accountability
-   Enable managers to oversee branch operations and staff activities

###  Non-functional Requirements

1.  Security
-   Implement role-based access control for system functions
-   Secure storage of personal information
-   Maintain audit logs of critical transactions
  
2.  Performance
-   Support concurrent operations from multiple branches
-   Ensure common queries execute quickly
-   Handle peak loads during busy periods

3.  Usability
-   Design database schema with clear naming conventions
-   Implement appropriate constraints for data integrity
-   Create an indexing strategy for frequently queried fields
    
4.  Scalability
-   Structure database to accommodate growing collection and user base
-   Design for easy addition of new library branches
-   Support backup and recovery processes
---


## 🧱 Planned Core Entities

1. Branch
-   Attributes: BranchID (PK), Name, Address, Phone, Email
-   Description: Library locations within the city system
    
2. Staff
-   Attributes: StaffID (PK), BranchID (FK), ManagerID (FK), FirstName, LastName, Email, Role
-   Description: Library employees with different roles and access levels

3. Patron
-   Attributes: PatronID (PK), FirstName, LastName, Email, Phone, RegistrationDate
-   Description: Library members who borrow books

4. Book
-   Attributes: BookID (PK), BranchID (FK), Title, Author, ISBN, Genre, Status, ShelfLocation
-   Description: Books in the library with location and availability information

5. Loan
-   Attributes: LoanID (PK), BookID (FK), PatronID (FK), StaffID (FK), CheckoutDate, DueDate, ReturnDate
-   Description: Records of books borrowed by patrons
    
6. Fine
-   Attributes: FineID (PK), LoanID (FK), Amount, IssueDate, PaymentStatus
-   Description: Financial penalties for late returns or damaged books

---


## 🔧 Technology Stack

| Layer                | Technology                   | Description |
|----------------------|------------------------------|-------------|
| Database System      | MySQL 8.0                    | Relational database for storing all structured data with support for constraints, triggers, stored procedures, indexing, and normalization. |
| Database Modeling    | MySQL Workbench              | Tool for designing the ER diagram, generating DDL scripts, and visualizing the physical and logical schema. |
| Backend Framework    | Flask (Python)               | Lightweight web framework for building the RESTful API, connecting the frontend with the MySQL database. |
| ORM & DB Integration | SQLAlchemy + Flask-MySQLdb or Flask-PyMySQL | Object-relational mapping for managing database models and connecting Flask with MySQL. |
| Authentication       | Flask-Login, Flask-Bcrypt, MySQL GRANT | Session management, password hashing, and database-level role-based access control. |
| Frontend             | HTML5, CSS3, JavaScript, Bootstrap 5 | Used for creating a responsive user interface with interactive elements for users and staff. |
| API Communication    | Fetch API           | Allows asynchronous frontend-to-backend requests for user actions like book checkouts, returns, and searches. |
| Data Visualization   | Chart.js                     | Frontend JavaScript library to visualize analytics such as borrowing trends, fine statistics, and top books. |
| Testing Tools        | Postman, Pytest              | Postman for API testing and Pytest for backend unit testing to ensure functional accuracy and reliability. |
| Performance Tuning   | MySQL EXPLAIN, Indexing, Partitioning | Tools and strategies to monitor, measure, and improve query performance for large-scale operations. |
| Deployment           | Localhost | Local development with optional cloud hosting for demo purposes. |
| Version Control      | Git, GitHub                  | For team collaboration, version tracking, issue management, and hosting project source code and documentation. |


---
## 👥 Team Members & Roles

| Role                   | Responsibilities | Assignee |
|------------------------|------------------|----------|
| Database Designer      | - Develop project requirements<br>- Design ER diagram (minimum 4 entities)<br>- Normalize schema up to 3NF<br>- Write DDL scripts with keys and constraints | Huy |
| SQL Expert             | - Create all required tables and relationships<br>- Implement at least one view<br>- Write at least two stored procedures<br>- Define at least one trigger | Kate |
| Web Designer           | - Design and implement the website UI<br>- Integrate web interface with MySQL database<br>- Implement data visualizations using analytics tools | Chi |
| Performance Optimizer  | - Apply indexing and/or partitioning<br>- Optimize queries and compare performance before/after<br>- Optionally simulate OLTP workloads | Huy |
| Security Expert        | - Assign user roles and privileges<br>- Use encryption for sensitive data (e.g., passwords)<br>- Prevent SQL injection using prepared statements | Kate |
| Tester                 | - Ensure full system functionality<br>- Conduct end-to-end testing<br>- Gather and document user feedback | Chi |

---

## 📅 Timeline & Milestones
All dates are for May 2025
| Task | Start | Finish |
|--|--|--|
| Conceptual & Physical Design | 7 | 10 |
| Frontend Development | 7 | 14 |
| Implementation of DB Entities | 10 | 14 |
| Security Configuration | 14 | 17 |
| Web Integration | 14 | 17 |
| Performance Tuning | 17 | 22 |
| End-to-End Testing | 22 | 27 |
| Final Documentation | 22 | 27 |

---
