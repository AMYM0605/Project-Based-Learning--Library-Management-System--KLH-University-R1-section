# LibSphere - Library Management System

## Overview
LibSphere is a secure, scalable Library Management System designed to efficiently manage library resources and streamline operations. It offers a robust backend, an intuitive frontend interface, and AI-powered features such as personalized book recommendations and predictive analytics. This system aims to improve user experience for both library staff and patrons while maintaining data integrity and security.

## Features
- User registration, authentication, and role-based access (admin, librarian, user)
- Comprehensive book catalog management with categories and availability tracking
- Book lending and return management with due date tracking and notifications
- AI-driven book recommendation engine based on user preferences and history
- Overdue book prediction and demand forecasting using machine learning
- Audit logging for tracking user actions and maintaining security
- Responsive and accessible frontend interface powered by React.js
- RESTful API backend built with Python Flask for efficient data management

## Technologies Used
- Programming Languages: Python, JavaScript, HTML, CSS
- Backend Framework: Flask
- Frontend Framework: React.js
- Database: MySQL / PostgreSQL (configurable)
- AIML: Machine learning models for recommendations and predictions
- Version Control: Git and GitHub

## Getting Started

### Prerequisites
- Git (to clone the repository)
- Python 3.x
- Node.js and npm (for frontend)
- MySQL or PostgreSQL server installed and running

### Installation

1. Clone the repository:
    
    git clone https://github.com/AMYM0605/Project-Based-Learning--Library-Management-System--KLH-University-R1-section.git
    cd Project-Based-Learning--Library-Management-System--KLH-University-R1-section
    

2. Set up the backend environment:
    
    cd backend
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    pip install -r requirements.txt
    

3. Configure database connection in the backend (e.g., update .env or config files):
    
    SQLALCHEMY_DATABASE_URI='mysql+pymysql://username:password@localhost/library_management'
    

4. Apply database migrations / create tables:
    
    flask db upgrade
    # Or manually run schema scripts if provided
    

5. Run the backend server:
    
    flask run
    

6. Set up and run the frontend:
    
    cd ../frontend
    npm install
    npm start
    

## Usage
- Access the frontend at http://localhost:3000/ (or configured port)
- Register as a user or login with provided credentials
- Navigate and search the book catalog
- Borrow and return books via the interface
- Receive notifications and personalized book recommendations powered by AIML

## Contribution
Contributions are welcome! Feel free to:
- Report bugs or open issues
- Suggest new features
- Submit pull requests with improvements or fixes

Please adhere to a friendly and collaborative code of conduct.

---

Thank you for exploring the LibSphere Library Management System!
