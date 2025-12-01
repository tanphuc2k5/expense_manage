from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    # SECRET_KEY và cấu hình DB
    app.config["SECRET_KEY"] = "change-this-secret-key"
    base_dir = os.path.abspath(os.path.dirname(__file__))
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir, "expense.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"

    from .models import User, Category

    # Đăng ký blueprints
    from .routes.auth import auth_bp
    from .routes.main import main_bp
    from .routes.expenses import expenses_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(expenses_bp)

    # Tạo DB + seed categories
    with app.app_context():
        db.create_all()

        # Seed danh mục mặc định nếu chưa có
        if Category.query.count() == 0:
            default_cats = [
                "Ăn uống",
                "Đi lại",
                "Nhà ở",
                "Giải trí",
                "Học tập",
                "Sức khỏe",
                "Lương",
                "Khác",
            ]
            for name in default_cats:
                c = Category(name=name)
                db.session.add(c)
            db.session.commit()

    return app
