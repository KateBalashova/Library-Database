# 📚 Library Management System
---

## 📄 Project Description

---

## 🎯 Functional & Non-functional Requirements

### Functional Requirements


###  Non-functional Requirements

---


## 🧱 Planned Core Entities

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

## 📅 Timeline & Milestones
