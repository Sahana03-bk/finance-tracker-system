# 💰 Finance Tracker System

A Python-powered finance tracking backend application built with **FastAPI**, **SQLite**, **SQLAlchemy**, and **Jinja2 templates**.  
This project is designed to manage financial records, generate summaries, and demonstrate **role-based access control** for different types of users.

## 📌 Project Overview

The **Finance Tracker System** is a backend-focused application created to help users manage and analyze financial records in a structured way.  
It allows storing transactions, viewing summaries of financial activity, and applying role-based behavior for different user types.

The system is designed to support a dashboard or finance management application where users can:

- Record income and expense transactions
- View financial summaries and analytics
- Access features based on user role
- Manage financial records securely and logically

This project focuses on **clean backend design**, **functional correctness**, and **clear role-based access control**, making it suitable for a Python backend internship assessment.


## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Programming Language | Python 3 |
| Backend Framework | FastAPI |
| Database | SQLite |
| ORM | SQLAlchemy |
| Template Engine | Jinja2 |
| Frontend | HTML, CSS |
| Server | Uvicorn |
| API Documentation | Swagger UI (FastAPI Docs) |

## ✨ Features Implemented

### 📌 Core Features
- User login system with role-based access
- Financial transaction management
- Create, view, update, and delete transaction records
- Filter transactions by type, category, and date range
- Search transactions by category or note
- Financial summary generation
- Category-wise breakdown of expenses and income
- Monthly totals overview
- Recent activity tracking
- Pagination for transaction listing
- Export transactions to JSON
- Export transactions to CSV
- API documentation using FastAPI Swagger UI

### 👥 Role-Based Features

#### 👁️ Viewer
- Can view transaction records
- Can view financial summary
- Can access recent activity and analytics
- Read-only access (no create, update, or delete)

#### 📊 Analyst
- Can view transaction records
- Can apply filters by type, category, and date range
- Can use search functionality for transaction analysis
- Can access financial summaries and detailed insights
- Read-only access for records (no create, update, or delete)

#### 🛠️ Admin
- Full access to transaction management
- Can create transactions
- Can update transactions
- Can delete transactions
- Can view all summaries and analytics
- Can manage records across the system

### 🚀 Additional Enhancements
- Clean dashboard-style frontend using Jinja templates
- Professional home page and login page UI
- Role-based buttons shown in frontend templates
- Validation for amount, transaction type, and date input
- Error handling for invalid requests and missing records
- Structured backend routes for API and template pages

## 📂 Project Structure

```bash
FINANCE_BACKEND/
│── finance.db
│── README.md
│── requirements.txt
│
├── app/
│   │── __init__.py
│   │── auth.py
│   │── database.py
│   │── main.py
│   │── models.py
│   │── schemas.py
│   │
│   ├── static/
│   │   └── style.css
│   │
│   └── templates/
│       ├── add_transaction.html
│       ├── base.html
│       ├── dashboard.html
│       ├── edit_transaction.html
│       ├── home.html
│       ├── login.html
│       ├── summary_page.html
│       └── transactions_page.html
│
└── venv/

📌 Important note for README
Including `venv/` in project structure is **optional**.

Usually in README, we **do not include `venv/`** because:
- it is local environment
- not part of source code
- usually ignored in GitHub

## ⚙️ Local Setup

Follow these steps to run the **Finance Tracker System** locally on your machine.

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Sahana03-bk/finance-backend.git
cd finance-backend
```

### 2️⃣ Create a virtual environment

```bash
python -m venv venv
```

### 3️⃣ Activate the virtual environment

**On Windows**
```bash
venv\Scripts\activate
```

**On Mac/Linux**
```bash
source venv/bin/activate
```

### 4️⃣ Install project dependencies

```bash
pip install -r requirements.txt
```

### 5️⃣ Run the FastAPI application

```bash
uvicorn app.main:app --reload
```

### 6️⃣ Open the application in your browser

- **Home Page:** http://127.0.0.1:8000/
- **Swagger API Docs:** http://127.0.0.1:8000/docs

### 7️⃣ Default Test Users (if using seeded/demo data)

Use these sample credentials to test different role-based behaviors:

| Role    | Username  | Password    |
|---------|-----------|-------------|
| Viewer  | viewer1   | viewer123   |
| Analyst | analyst1  | analyst123  |
| Admin   | admin1    | admin123    |

> If you changed these credentials in your database, use your current values instead.

