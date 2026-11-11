from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, g
from app.models import db, User, Professional

auth_bp = Blueprint('auth', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or session.get('role') != 'admin':
            flash("Ushbu bo‘lim faqat administratorlar uchun mo‘ljallangan.", "error")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def pro_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id') or session.get('role') != 'professional':
            flash("Ushbu bo‘lim faqat mutaxassislar uchun mo‘ljallangan.", "error")
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        if session.get('role') == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif session.get('role') == 'professional':
            return redirect(url_for('pro.dashboard'))
        return redirect(url_for('main.home'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session.clear()
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            session['full_name'] = user.full_name

            if user.role == 'professional' and user.professional:
                session['pro_id'] = user.professional.id

            next_page = request.args.get('next')
            if user.role == 'admin':
                return redirect(next_page or url_for('admin.dashboard'))
            elif user.role == 'professional':
                return redirect(next_page or url_for('pro.dashboard'))
            else:
                return redirect(next_page or url_for('main.home'))
        else:
            error = "Login yoki parol noto'g'ri kiritildi."

    return render_template('login.html', error=error)

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.home'))
