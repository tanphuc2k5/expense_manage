from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import login_required, current_user
from datetime import datetime, date
from sqlalchemy import func

from ..models import Expense, Category
from .. import db

expenses_bp = Blueprint("expenses", __name__, url_prefix="/expenses")


def parse_date(date_str: str) -> date | None:
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


# ==========================
#       ADD EXPENSE
# ==========================
@expenses_bp.route("/add", methods=["GET", "POST"])
@login_required
def add():
    categories = Category.query.order_by(Category.name.asc()).all()

    if request.method == "POST":
        type_ = request.form.get("type")
        amount_str = request.form.get("amount", "").strip()
        note = request.form.get("note", "").strip()
        date_str = request.form.get("date", "").strip()
        category_id = request.form.get("category_id")

        if not type_ or not amount_str or not date_str or not category_id:
            flash("Vui lòng nhập đầy đủ thông tin bắt buộc.", "danger")
            return redirect(url_for("expenses.add"))

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash("Số tiền phải là số dương.", "danger")
            return redirect(url_for("expenses.add"))

        date_val = parse_date(date_str)
        if not date_val:
            flash("Ngày không hợp lệ.", "danger")
            return redirect(url_for("expenses.add"))

        expense = Expense(
            type=type_,
            amount=amount,
            note=note,
            date=date_val,
            user_id=current_user.id,
            category_id=int(category_id),
        )
        db.session.add(expense)
        db.session.commit()

        flash("Thêm chi tiêu/thu nhập thành công.", "success")
        return redirect(url_for("main.index"))

    return render_template("expense_form.html", mode="add", categories=categories)


# ==========================
#        EDIT EXPENSE
# ==========================
@expenses_bp.route("/<int:expense_id>/edit", methods=["GET", "POST"])
@login_required
def edit(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    categories = Category.query.order_by(Category.name.asc()).all()

    if request.method == "POST":
        type_ = request.form.get("type")
        amount_str = request.form.get("amount", "").strip()
        note = request.form.get("note", "").strip()
        date_str = request.form.get("date", "").strip()
        category_id = request.form.get("category_id")

        if not type_ or not amount_str or not date_str or not category_id:
            flash("Vui lòng nhập đầy đủ thông tin bắt buộc.", "danger")
            return redirect(url_for("expenses.edit", expense_id=expense_id))

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            flash("Số tiền phải là số dương.", "danger")
            return redirect(url_for("expenses.edit", expense_id=expense_id))

        date_val = parse_date(date_str)
        if not date_val:
            flash("Ngày không hợp lệ.", "danger")
            return redirect(url_for("expenses.edit", expense_id=expense_id))

        expense.type = type_
        expense.amount = amount
        expense.note = note
        expense.date = date_val
        expense.category_id = int(category_id)

        db.session.commit()
        flash("Cập nhật chi tiêu thành công.", "success")
        return redirect(url_for("expenses.detail", expense_id=expense.id))

    return render_template(
        "expense_form.html",
        mode="edit",
        expense=expense,
        categories=categories,
    )


# ==========================
#       DELETE EXPENSE
# ==========================
@expenses_bp.route("/<int:expense_id>/delete", methods=["POST"])
@login_required
def delete(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    db.session.delete(expense)
    db.session.commit()
    flash("Đã xóa khoản chi tiêu.", "warning")
    return redirect(url_for("main.index"))


# ==========================
#       DETAIL VIEW
# ==========================
@expenses_bp.route("/<int:expense_id>")
@login_required
def detail(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first_or_404()
    return render_template("expense_detail.html", expense=expense)


# ==========================
#      MONTHLY REPORT
# ==========================
@expenses_bp.route("/month")
@login_required
def by_month():
    today = date.today()
    month = request.args.get("month", type=int) or today.month
    year = request.args.get("year", type=int) or today.year

    q = Expense.query.filter(
        Expense.user_id == current_user.id,
        func.extract("month", Expense.date) == month,
        func.extract("year", Expense.date) == year,
    ).order_by(Expense.date.desc(), Expense.id.desc())

    expenses = q.all()

    total_income = sum(e.amount for e in expenses if e.type == "Income")
    total_expense = sum(e.amount for e in expenses if e.type == "Expense")

    category_stats = (
        db.session.query(Category.name, func.sum(Expense.amount))
        .join(Expense, Expense.category_id == Category.id)
        .filter(
            Expense.user_id == current_user.id,
            Expense.type == "Expense",
            func.extract("month", Expense.date) == month,
            func.extract("year", Expense.date) == year,
        )
        .group_by(Category.id)
        .all()
    )

    return render_template(
        "expenses_month.html",
        expenses=expenses,
        month=month,
        year=year,
        total_income=total_income,
        total_expense=total_expense,
        category_stats=category_stats,
    )


# ==========================
#   TOTAL EXPENSE REPORT
# ==========================
@expenses_bp.route("/report")
@login_required
def report():
    expenses = Expense.query.filter_by(user_id=current_user.id).all()

    total_income = sum(e.amount for e in expenses if e.type == "Income")
    total_expense = sum(e.amount for e in expenses if e.type == "Expense")
    balance = total_income - total_expense

    category_stats = (
        db.session.query(Category.name, func.sum(Expense.amount))
        .join(Expense, Expense.category_id == Category.id)
        .filter(
            Expense.user_id == current_user.id,
            Expense.type == "Expense",
        )
        .group_by(Category.id)
        .all()
    )

    return render_template(
        "expenses_report.html",
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        category_stats=category_stats,
    )
