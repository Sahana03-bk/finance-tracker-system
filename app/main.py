from pathlib import Path

from fastapi import FastAPI, Request, Depends, HTTPException, Form, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import Base, engine
import app.models  # Important: ensures models are registered before create_all
from app import models, schemas
from app.auth import get_db, hash_password, login_user, get_current_user, require_roles, active_tokens
from datetime import date

from datetime import datetime

import csv
import io
import json
from fastapi.responses import StreamingResponse

BASE_DIR = Path(__file__).resolve().parent

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance Tracker System")

# Static files
app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

# Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html",
        context={"request": request}
    )


@app.get("/login-page", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"request": request, "error": None, "success": None}
    )


@app.post("/login-page", response_class=HTMLResponse)
def login_page_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    token = login_user(db, username, password)

    if not token:
        return templates.TemplateResponse(
            request=request,
            name="login.html",
            context={
                "request": request,
                "error": "Invalid username or password",
                "success": None
            }
        )

    # Get logged-in user
    user = db.query(models.User).filter(models.User.username == username).first()

    # Save login activity
    if user:
        login_activity = models.LoginActivity(
            user_id=user.id,
            username=user.username,
            role=user.role,
            status="Logged In"
        )
        db.add(login_activity)
        db.commit()

    return RedirectResponse(
        url=f"/dashboard?username={username}",
        status_code=303
    )

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    login_activities = []

    # Only admin can see analyst/viewer login activity
    if user.role.lower() == "admin":
        login_activities = (
            db.query(models.LoginActivity)
            .filter(models.LoginActivity.role.in_(["analyst", "viewer"]))
            .order_by(models.LoginActivity.login_time.desc())
            .limit(10)
            .all()
        )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "request": request,
            "user": user,
            "login_activities": login_activities
        }
    )


@app.get("/recent-activity", response_class=HTMLResponse)
def recent_activity_page(
    request: Request,
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only admin can access this page
    if user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="You do not have permission to view recent activity")

    login_activities = (
        db.query(models.LoginActivity)
        .filter(models.LoginActivity.role.in_(["analyst", "viewer"]))
        .order_by(models.LoginActivity.login_time.desc())
        .all()
    )

    return templates.TemplateResponse(
        request=request,
        name="recent_activity.html",
        context={
            "request": request,
            "user": user,
            "login_activities": login_activities
        }
    )

@app.get("/transactions-page", response_class=HTMLResponse)
def transactions_page(
    request: Request,
    username: str,
    type: str = Query(None),
    category: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    search: str = Query(None),
    page: int = Query(1),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # All roles can view all transactions
    query = db.query(models.Transaction)

    # Only Analyst and Admin can apply filters and search
    if user.role.lower() in ["analyst", "admin"]:
        if type:
            query = query.filter(models.Transaction.type == type)

        if category:
            query = query.filter(models.Transaction.category.ilike(f"%{category}%"))

        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.filter(models.Transaction.date >= parsed_start_date)
            except ValueError:
                pass

        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.filter(models.Transaction.date <= parsed_end_date)
            except ValueError:
                pass

        # Search in category or note
        if search:
            query = query.filter(
                (models.Transaction.category.ilike(f"%{search}%")) |
                (models.Transaction.note.ilike(f"%{search}%"))
            )

    # Pagination settings
    per_page = 5
    total_records = query.count()
    total_pages = (total_records + per_page - 1) // per_page

    if page < 1:
        page = 1
    if total_pages > 0 and page > total_pages:
        page = total_pages

    transactions = query.order_by(
        models.Transaction.date.desc(),
        models.Transaction.id.desc()
    ).offset((page - 1) * per_page).limit(per_page).all()

    return templates.TemplateResponse(
        request=request,
        name="transactions_page.html",
        context={
            "request": request,
            "user": user,
            "transactions": transactions,
            "selected_type": type or "",
            "selected_category": category or "",
            "selected_start_date": start_date or "",
            "selected_end_date": end_date or "",
            "selected_search": search or "",
            "current_page": page,
            "total_pages": total_pages
        }
    )

@app.get("/edit-transaction/{transaction_id}", response_class=HTMLResponse)
def edit_transaction_page(
    request: Request,
    transaction_id: int,
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="You do not have permission to edit transactions")

    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return templates.TemplateResponse(
        request=request,
        name="edit_transaction.html",
        context={
            "request": request,
            "user": user,
            "transaction": transaction,
            "error": None,
            "success": None
        }
    )

@app.get("/add-transaction", response_class=HTMLResponse)
def add_transaction_page(
    request: Request,
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="You do not have permission to access this page")

    return templates.TemplateResponse(
        request=request,
        name="add_transaction.html",
        context={
            "request": request,
            "user": user,
            "error": None,
            "success": None
        }
    )

@app.post("/edit-transaction/{transaction_id}", response_class=HTMLResponse)
def edit_transaction_submit(
    request: Request,
    transaction_id: int,
    username: str = Query(...),
    amount: float = Form(...),
    type: str = Form(...),
    category: str = Form(...),
    date: str = Form(...),
    note: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="You do not have permission to update transactions")

    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if amount <= 0:
        return templates.TemplateResponse(
            request=request,
            name="edit_transaction.html",
            context={
                "request": request,
                "user": user,
                "transaction": transaction,
                "error": "Amount must be greater than 0",
                "success": None
            }
        )

    if type not in ["income", "expense"]:
        return templates.TemplateResponse(
            request=request,
            name="edit_transaction.html",
            context={
                "request": request,
                "user": user,
                "transaction": transaction,
                "error": "Type must be either income or expense",
                "success": None
            }
        )

    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return templates.TemplateResponse(
            request=request,
            name="edit_transaction.html",
            context={
                "request": request,
                "user": user,
                "transaction": transaction,
                "error": "Invalid date format",
                "success": None
            }
        )

    transaction.amount = amount
    transaction.type = type
    transaction.category = category
    transaction.date = parsed_date
    transaction.note = note

    db.commit()
    db.refresh(transaction)

    return templates.TemplateResponse(
        request=request,
        name="edit_transaction.html",
        context={
            "request": request,
            "user": user,
            "transaction": transaction,
            "error": None,
            "success": "Transaction updated successfully!"
        }
    )

  


@app.post("/delete-transaction/{transaction_id}", response_class=HTMLResponse)
def delete_transaction_page(
    request: Request,
    transaction_id: int,
    username: str = Query(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role.lower() != "admin":
        raise HTTPException(status_code=403, detail="You do not have permission to delete transactions")

    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()

    return RedirectResponse(
        url=f"/transactions-page?username={username}",
        status_code=303)


@app.post("/add-transaction", response_class=HTMLResponse)
def add_transaction_submit(
    request: Request,
    username: str = Query(...),
    amount: float = Form(...),
    type: str = Form(...),
    category: str = Form(...),
    date: str = Form(...),
    note: str = Form(...),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only admin can add transaction
    if user.role.lower() != "admin":
        return templates.TemplateResponse(
            request=request,
            name="add_transaction.html",
            context={
                "request": request,
                "user": user,
                "error": "You do not have permission to add transactions",
                "success": None
            }
        )

    if amount <= 0:
        return templates.TemplateResponse(
            request=request,
            name="add_transaction.html",
            context={
                "request": request,
                "user": user,
                "error": "Amount must be greater than 0",
                "success": None
            }
        )

    if type not in ["income", "expense"]:
        return templates.TemplateResponse(
            request=request,
            name="add_transaction.html",
            context={
                "request": request,
                "user": user,
                "error": "Type must be either income or expense",
                "success": None
            }
        )

    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        return templates.TemplateResponse(
            request=request,
            name="add_transaction.html",
            context={
                "request": request,
                "user": user,
                "error": "Invalid date format",
                "success": None
            }
        )

    new_transaction = models.Transaction(
        amount=amount,
        type=type,
        category=category,
        date=parsed_date,
        note=note,
        user_id=user.id
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return templates.TemplateResponse(
        request=request,
        name="add_transaction.html",
        context={
            "request": request,
            "user": user,
            "error": None,
            "success": "Transaction added successfully!"
        }
    )


@app.get("/export-transactions-csv")
def export_transactions_csv(
    username: str,
    type: str = Query(None),
    category: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(models.Transaction)

    # Only Analyst and Admin can use filters/search in export
    if user.role.lower() in ["analyst", "admin"]:
        if type:
            query = query.filter(models.Transaction.type == type)

        if category:
            query = query.filter(models.Transaction.category.ilike(f"%{category}%"))

        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.filter(models.Transaction.date >= parsed_start_date)
            except ValueError:
                pass

        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.filter(models.Transaction.date <= parsed_end_date)
            except ValueError:
                pass

        if search:
            query = query.filter(
                (models.Transaction.category.ilike(f"%{search}%")) |
                (models.Transaction.note.ilike(f"%{search}%"))
            )

    transactions = query.order_by(
        models.Transaction.date.desc(),
        models.Transaction.id.desc()
    ).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow(["ID", "Amount", "Type", "Category", "Date", "Note", "User ID"])

    # Data rows
    for t in transactions:
        writer.writerow([
            t.id,
            t.amount,
            t.type,
            t.category,
            t.date,
            t.note,
            t.user_id
        ])

    output.seek(0)

    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=transactions_export.csv"}
    )

@app.get("/export-transactions-json")
def export_transactions_json(
    username: str,
    type: str = Query(None),
    category: str = Query(None),
    start_date: str = Query(None),
    end_date: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    query = db.query(models.Transaction)

    # Only Analyst and Admin can use filters/search in export
    if user.role.lower() in ["analyst", "admin"]:
        if type:
            query = query.filter(models.Transaction.type == type)

        if category:
            query = query.filter(models.Transaction.category.ilike(f"%{category}%"))

        if start_date:
            try:
                parsed_start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
                query = query.filter(models.Transaction.date >= parsed_start_date)
            except ValueError:
                pass

        if end_date:
            try:
                parsed_end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                query = query.filter(models.Transaction.date <= parsed_end_date)
            except ValueError:
                pass

        if search:
            query = query.filter(
                (models.Transaction.category.ilike(f"%{search}%")) |
                (models.Transaction.note.ilike(f"%{search}%"))
            )

    transactions = query.order_by(
        models.Transaction.date.desc(),
        models.Transaction.id.desc()
    ).all()

    data = [
        {
            "id": t.id,
            "amount": t.amount,
            "type": t.type,
            "category": t.category,
            "date": str(t.date),
            "note": t.note,
            "user_id": t.user_id
        }
        for t in transactions
    ]

    json_content = json.dumps(data, indent=4)

    return StreamingResponse(
        io.StringIO(json_content),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=transactions_export.json"}
    )


@app.get("/summary-page", response_class=HTMLResponse)
def summary_page(
    request: Request,
    username: str,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == username).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # All roles can view overall summary
    transactions = db.query(models.Transaction).all()

    # Total income
    total_income = sum(t.amount for t in transactions if t.type == "income")

    # Total expenses
    total_expenses = sum(t.amount for t in transactions if t.type == "expense")

    # Current balance
    current_balance = total_income - total_expenses

    # Total transactions
    total_transactions = len(transactions)

    # Category breakdown
    category_totals = {}
    for t in transactions:
        category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

    category_breakdown = [
        {"category": category, "total": total}
        for category, total in category_totals.items()
    ]

    # Monthly totals
    monthly_totals_dict = {}
    for t in transactions:
        month_key = t.date.strftime("%Y-%m")
        monthly_totals_dict[month_key] = monthly_totals_dict.get(month_key, 0) + t.amount

    monthly_totals = [
        {"month": month, "total": total}
        for month, total in sorted(monthly_totals_dict.items())
    ]

    # Recent activity (latest 5)
    recent_activity = sorted(transactions, key=lambda x: (x.date, x.id), reverse=True)[:5]

    # Chart data
    category_labels = [item["category"] for item in category_breakdown]
    category_values = [float(item["total"]) for item in category_breakdown]

    monthly_labels = [item["month"] for item in monthly_totals]
    monthly_values = [float(item["total"]) for item in monthly_totals]

    return templates.TemplateResponse(
        request=request,
        name="summary_page.html",
        context={
            "request": request,
            "user": user,
            "total_income": total_income,
            "total_expenses": total_expenses,
            "current_balance": current_balance,
            "total_transactions": total_transactions,
            "category_breakdown": category_breakdown,
            "monthly_totals": monthly_totals,
            "recent_activity": recent_activity,
            "category_labels": category_labels,
            "category_values": category_values,
            "monthly_labels": monthly_labels,
            "monthly_values": monthly_values
        }
    )
# ----------------------------
# Authentication APIs
# ----------------------------

@app.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = models.User(
        username=user.username,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    token = login_user(db, user.username, user.password)

    if not token:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    db_user = db.query(models.User).filter(models.User.username == user.username).first()

    # Save login activity
    if db_user:
        login_activity = models.LoginActivity(
            user_id=db_user.id,
            username=db_user.username,
            role=db_user.role,
            status="Logged In"
        )
        db.add(login_activity)
        db.commit()

    return {
        "message": "Login successful",
        "token": token,
        "username": db_user.username,
        "role": db_user.role
    }
# ----------------------------
# Protected Test APIs
# ----------------------------

@app.get("/me")
def get_me(current_user: models.User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "username": current_user.username,
        "role": current_user.role
    }


@app.get("/admin-only")
def admin_only(current_user: models.User = Depends(require_roles(["admin"]))):
    return {
        "message": f"Welcome Admin {current_user.username}! You have access."
    }

@app.get("/me-test")
def get_me_test(token: str, db: Session = Depends(get_db)):
    user_id = active_tokens.get(token)

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user.id,
        "username": user.username,
        "role": user.role
    }

# ----------------------------
# Transaction APIs
# ----------------------------





@app.get("/transactions/{transaction_id}", response_model=schemas.TransactionResponse)
def get_transaction_by_id(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["viewer", "analyst", "admin"]))
):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


@app.put("/transactions/{transaction_id}", response_model=schemas.TransactionResponse)
def update_transaction(
    transaction_id: int,
    updated_data: schemas.TransactionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.amount = updated_data.amount
    transaction.type = updated_data.type
    transaction.category = updated_data.category
    transaction.date = updated_data.date
    transaction.note = updated_data.note

    db.commit()
    db.refresh(transaction)

    return transaction


@app.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["admin"]))
):
    transaction = db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()

    return {"message": "Transaction deleted successfully"}

# ----------------------------
# Summary & Analytics API
# ----------------------------

@app.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(require_roles(["viewer", "analyst", "admin"]))
):
    # Viewer sees only their own transactions
    if current_user.role.lower() == "viewer":
        transactions = db.query(models.Transaction).filter(
            models.Transaction.user_id == current_user.id
        ).all()
    else:
        # Analyst and Admin see all transactions
        transactions = db.query(models.Transaction).all()

    # Total income
    total_income = sum(t.amount for t in transactions if t.type == "income")

    # Total expenses
    total_expenses = sum(t.amount for t in transactions if t.type == "expense")

    # Current balance
    current_balance = total_income - total_expenses

    # Category breakdown
    category_totals = {}
    for t in transactions:
        category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

    category_breakdown = [
        {"category": category, "total": total}
        for category, total in category_totals.items()
    ]

    # Monthly totals
    monthly_totals_dict = {}
    for t in transactions:
        month_key = t.date.strftime("%Y-%m")
        monthly_totals_dict[month_key] = monthly_totals_dict.get(month_key, 0) + t.amount

    monthly_totals = [
        {"month": month, "total": total}
        for month, total in monthly_totals_dict.items()
    ]

    # Recent activity (latest 5)
    recent_activity = sorted(transactions, key=lambda x: (x.date, x.id), reverse=True)[:5]

    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "current_balance": current_balance,
        "category_breakdown": category_breakdown,
        "monthly_totals": monthly_totals,
        "recent_activity": [
            {
                "id": t.id,
                "amount": t.amount,
                "type": t.type,
                "category": t.category,
                "date": str(t.date),
                "note": t.note,
                "user_id": t.user_id
            }
            for t in recent_activity
        ]
    }