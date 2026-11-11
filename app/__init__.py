import os
from flask import Flask, render_template
from app.config import Config
from app.models import db
from app.database import seed_database

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Ensure instance and upload directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    if 'sqlite' in app.config['SQLALCHEMY_DATABASE_URI']:
        os.makedirs(os.path.join(app.root_path, '..', 'instance'), exist_ok=True)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.booking import booking_bp
    from app.routes.auth import auth_bp
    from app.routes.pro import pro_bp
    from app.routes.admin import admin_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(booking_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(pro_bp)
    app.register_blueprint(admin_bp)

    # Custom template filters
    @app.template_filter('currency')
    def currency_filter(amount):
        try:
            return "{:,}".format(int(amount)).replace(',', ' ') + " so'm"
        except (ValueError, TypeError):
            return str(amount)

    # Custom 404 and 500 error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('base.html', content_override="<div class='container section-spacing' style='text-align:center;'><h1>404</h1><p>Sahifa topilmadi</p><a href='/' class='btn btn-gold' style='margin-top:1.5rem;'>Bosh sahifa</a></div>"), 404

    @app.errorhandler(500)
    def server_error(e):
        return render_template('base.html', content_override="<div class='container section-spacing' style='text-align:center;'><h1>500</h1><p>Serverda kutilmagan xatolik yuz berdi</p><a href='/' class='btn btn-gold' style='margin-top:1.5rem;'>Bosh sahifa</a></div>"), 500

    # Initialize and seed database
    with app.app_context():
        db.create_all()
        # Seed if empty
        seed_database()

    return app
