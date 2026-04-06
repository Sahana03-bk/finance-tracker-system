# 💰 Finance Tracker System

A **role-based Finance Tracker web application** built using **FastAPI, SQLAlchemy, SQLite, Jinja2 Templates, HTML, CSS, and JavaScript**.

This project provides secure user authentication, role-based access control, financial transaction management, dashboard pages, analytics, search/filtering, exports, and recent activity tracking through both **REST APIs** and a **professional web interface**

---

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

## 📂 Project Structure

```bash
finance-tracker-system/
│── app/
│   │── __init__.py
│   │── main.py
│   │── models.py
│   │── schemas.py
│   │── database.py
│   │── auth.py
│   │
│   ├── templates/
│   │   │── base.html
│   │   │── home.html
│   │   │── login_page.html
│   │   │── dashboard.html
│   │   │── add_transaction.html
│   │   │── transactions_page.html
│   │   │── edit_transaction.html
│   │   │── summary_page.html
│   │   │── recent_activity.html
│   │
│   ├── static/
│   │   │── style.css
│
│── requirements.txt
│── README.md
```

## 🚀 Project Overview

The **Finance Tracker System** is a backend-focused internship project with a modern frontend interface.

It supports:

- **User Registration & Login**
- **JWT Authentication**
- **Role-Based Authorization** (`admin`, `analyst`, `viewer`)
- **Transaction Management (CRUD)**
- **Role-Based Dashboard**
- **Transaction Search, Filters & Pagination**
- **Financial Summary & Analytics**
- **Charts & Visualizations**
- **Recent Login Activity Tracking**
- **CSV / JSON Export**
- **FastAPI Swagger API Docs**

This project is designed to go beyond a basic CRUD app by including **role-based restrictions**, **professional dashboard UI**, **summary analytics**, and **audit-style recent activity tracking**.

---

## ✨ Features

### 🔐 Authentication & Security
- User Registration API
- User Login API
- JWT Access Token generation
- OAuth2 Bearer token authentication
- Protected endpoints using authentication
- Secure role-based route access

### 💳 Transaction Management
- Add transactions
- View transactions
- Edit transactions
- Delete transactions
- Transaction validation
- Income / Expense classification
- Category-based organization

### 🔍 Search, Filters & Pagination
- Search transactions by keyword
- Filter by transaction type
- Filter by category
- Filter by date range
- Paginated transaction listing
- Cleaner browsing for large data sets

### 📊 Analytics & Summary
- Total Income
- Total Expenses
- Net Balance
- Total Records
- Monthly Financial Trend
- Category-wise Expense Distribution
- Recent Financial Activity
- Chart.js based data visualization

### 📤 Export Features
- Export transactions as **CSV**
- Export transactions as **JSON**

### 🕒 Recent Activity Tracking
- Admin can monitor recent login activity
- Shows username, role, date, time, and status

---


✨ Features

## 👥 Role-Based Access Control

The system supports **3 fixed roles**:

### 1️⃣ Admin
**Full access to the system**

Admin can:
- Add transactions
- Edit transactions
- Delete transactions
- View all transactions
- Apply search and filters
- View financial summary
- View recent login activity of users
- Export transaction data
- Access admin-only API routes

---

### 2️⃣ Analyst
**Analysis-focused access**

Analyst can:
- View all transactions
- Apply search and filters
- View financial summary
- Access dashboard insights

Analyst cannot:
- Add transactions
- Delete transactions
- Access admin-only features

---

### 3️⃣ Viewer
**Read-only access**

Viewer can:
- View dashboard
- View transactions
- View summary

Viewer cannot:
- Add transactions
- Edit transactions
- Delete transactions
- Access admin-only routes

---

## 🖥️ Dashboard Pages

The project includes a professional **role-based dashboard interface** built with **Jinja2 templates + HTML + CSS**.

### Available UI Pages

- `/` → **Home Page**
- `/login-page` → **Login Page**
- `/dashboard` → **Role-Based Dashboard**
- `/add-transaction` → **Add Transaction Page** (Admin only)
- `/transactions-page` → **Transactions Page** (Search + Filters + Pagination)
- `/edit-transaction/{transaction_id}` → **Edit Transaction Page** (Admin only)
- `/summary-page` → **Financial Summary Page**
- `/recent-activity` → **Recent Login Activity Page** (Admin only)
- `/docs` → **Swagger API Documentation**

### Dashboard Navigation Includes
- Dashboard
- Add Transaction (Admin only)
- View Transactions
- Apply Filters (Admin & Analyst)
- View Summary
- Recent Activity (Admin only)
- API Docs
- Go Home

### Dashboard UI Highlights
- Sidebar navigation
- Top profile section
- User role badge
- Profile dropdown
- Quick action cards
- Role-based menu visibility
- Professional finance-themed design

---

## 📌 API Endpoints

### 👥 User Management Endpoints

#### 1️⃣ Register User
**Endpoint:** `POST /register`

**Description:**  
Creates a new user with username, password, and role.

**Roles Allowed:** Public

---

#### 2️⃣ Login User
**Endpoint:** `POST /login`

**Description:**  
Authenticates a user and returns a JWT access token.

**Roles Allowed:** Public

---

#### 3️⃣ Get Current User
**Endpoint:** `GET /me`

**Description:**  
Returns the authenticated user details.

**Roles Allowed:** Authenticated Users

---

#### 4️⃣ Admin-Only Access Check
**Endpoint:** `GET /admin-only`

**Description:**  
Allows access only to admin users.

**Roles Allowed:** Admin

---

#### 5️⃣ Test Authenticated User
**Endpoint:** `GET /me-test`

**Description:**  
Simple protected endpoint to verify authentication flow.

**Roles Allowed:** Authenticated Users

---

### 💳 Transaction Management Endpoints

#### 6️⃣ Get Transaction by ID
**Endpoint:** `GET /transactions/{transaction_id}`

**Description:**  
Fetches a specific transaction by its ID.

**Roles Allowed:** Authenticated Users (based on access rules)

---

#### 7️⃣ Update Transaction
**Endpoint:** `PUT /transactions/{transaction_id}`

**Description:**  
Updates an existing transaction.

**Roles Allowed:** Admin

---

#### 8️⃣ Delete Transaction
**Endpoint:** `DELETE /transactions/{transaction_id}`

**Description:**  
Deletes a transaction.

**Roles Allowed:** Admin

---

### 📊 Summary Endpoint

#### 9️⃣ Financial Summary API
**Endpoint:** `GET /summary`

**Description:**  
Returns:
- Total Income
- Total Expenses
- Current Balance
- Category Breakdown
- Monthly Totals
- Recent Financial Activity

**Roles Allowed:** Authenticated Users

---

## 💳 Transaction Management Details

### Add Transaction
- Admin can create new financial transactions
- Fields include:
  - Amount
  - Type (`income` / `expense`)
  - Category
  - Date
  - Note

### View Transactions
- Displays transactions in a professional table layout
- Supports:
  - Search by keyword
  - Filters
  - Pagination
  - Role-based visibility
  - Edit / Delete actions (Admin only)

### Edit Transaction
- Admin can update:
  - Amount
  - Type
  - Category
  - Date
  - Note

### Delete Transaction
- Admin can remove records securely

---

## 📊 Analytics / Summary

The **Summary Page** provides a visually enhanced analytics dashboard.

### Summary Cards
- **Total Income**
- **Total Expenses**
- **Net Balance**
- **Total Records**

### Charts & Visualizations
- **Monthly Financial Trend**
- **Category-wise Expense Distribution**
- **Interactive Chart.js charts**
- Clean professional analytics layout

### Data Sections
- Category-wise Breakdown
- Monthly Totals
- Recent Financial Activity (latest records)

### Summary Benefits
- Makes the project more professional than a basic CRUD app
- Provides visual understanding of financial data
- Helps users quickly analyze income and expense behavior

---

## 🕒 Recent Activity

A dedicated **Recent Activity** page is available for **Admin users**.

### Tracks:
- Username
- Role
- Login Date
- Login Time
- Status

### Why this feature is strong
- Adds audit-style visibility
- Makes role-based system look more professional
- Helps admin monitor analyst/viewer access
- Improves project quality for internship/demo

---

## 📤 Export Features

The project supports exporting transaction data in:

- **CSV format**
- **JSON format**

### Export Routes
- `/export-transactions-csv`
- `/export-transactions-json`

### Benefits
- Useful for reporting
- Helpful for data portability
- Supports external analysis
- Makes the project look more complete and practical

---

## 🔐 Authentication Flow

### Login Process
1. User logs in using username and password
2. JWT token is generated
3. Token is used to access protected API routes
4. Role is checked before granting access to restricted endpoints

### Protected API Examples
- `/me`
- `/admin-only`
- `/me-test`
- `/transactions/{transaction_id}`
- `/summary`

---

## ⚙️ Installation Steps

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/Sahana03-bk/finance-tracker-system.git
cd finance-tracker-system

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

