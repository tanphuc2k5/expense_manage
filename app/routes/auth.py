from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
from .. import db

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        # Validation
        if not username or not password or not confirm:
            flash("Vui lòng nhập đầy đủ thông tin.", "danger")
            return redirect(url_for("auth.register"))

        if password != confirm:
            flash("Mật khẩu nhập lại không khớp.", "danger")
            return redirect(url_for("auth.register"))

        existing = User.query.filter_by(username=username).first()
        if existing:
            flash("Tên đăng nhập đã tồn tại, hãy chọn tên khác.", "warning")
            return redirect(url_for("auth.register"))

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Đăng ký thành công! Hãy đăng nhập.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Đăng nhập thành công.", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))
        else:
            flash("Sai tên đăng nhập hoặc mật khẩu.", "danger")
            return redirect(url_for("auth.login"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Đã đăng xuất.", "info")
    return redirect(url_for("auth.login"))
