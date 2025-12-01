from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from ..models import Expense
from .. import db
from sqlalchemy import func
from datetime import date

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def index():
    # Thống kê tổng thu/chi/số dư cho toàn bộ dữ liệu
    total_income = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0.0))
        .filter_by(user_id=current_user.id, type="Income")
        .scalar()
    )
    total_expense = (
        db.session.query(func.coalesce(func.sum(Expense.amount), 0.0))
        .filter_by(user_id=current_user.id, type="Expense")
        .scalar()
    )
    balance = total_income - total_expense

    # Lấy 10 khoản mới nhất
    recent_expenses = (
        Expense.query.filter_by(user_id=current_user.id)
        .order_by(Expense.date.desc(), Expense.id.desc())
        .limit(10)
        .all()
    )

    # Mặc định thống kê tháng hiện tại cho biểu đồ
    today = date.today()
    current_month = today.month
    current_year = today.year

    monthly_expenses = (
        Expense.query.filter(
            Expense.user_id == current_user.id,
            func.extract("month", Expense.date) == current_month,
            func.extract("year", Expense.date) == current_year,
        ).all()
    )

    monthly_income = sum(e.amount for e in monthly_expenses if e.type == "Income")
    monthly_expense = sum(e.amount for e in monthly_expenses if e.type == "Expense")

    return render_template(
        "index.html",
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        expenses=recent_expenses,
        monthly_income=monthly_income,
        monthly_expense=monthly_expense,
    )
