import os
from datetime import datetime, date
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from app.models import (
    db, Professional, Service, ServiceCategory, Appointment,
    NotificationLog, StudioSetting, Review, User
)
from app.routes.auth import admin_required
from app.services.booking import update_booking_status
from app.services.notifications import TelegramNotifier

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    professionals = Professional.query.order_by(Professional.sort_order.asc()).all()
    services = Service.query.order_by(Service.sort_order.asc()).all()
    
    # Filter appointments
    pro_filter = request.args.get('pro_id', type=int)
    status_filter = request.args.get('status')
    
    query = Appointment.query
    if pro_filter:
        query = query.filter(Appointment.professional_id == pro_filter)
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
        
    appointments = query.order_by(Appointment.appointment_date.desc(), Appointment.start_time.desc()).all()
    
    # Metrics
    total_bookings = Appointment.query.count()
    pending_bookings = Appointment.query.filter_by(status='pending').count()
    confirmed_bookings = Appointment.query.filter(Appointment.status.in_(['confirmed', 'accepted'])).count()
    completed_bookings = Appointment.query.filter_by(status='completed').count()
    total_revenue = db.session.query(db.func.sum(Appointment.price)).filter(Appointment.status.in_(['confirmed', 'completed'])).scalar() or 0
    
    # Notification logs
    recent_logs = NotificationLog.query.order_by(NotificationLog.created_at.desc()).limit(15).all()
    
    return render_template(
        'admin/dashboard.html',
        professionals=professionals,
        services=services,
        appointments=appointments,
        total_bookings=total_bookings,
        pending_bookings=pending_bookings,
        confirmed_bookings=confirmed_bookings,
        completed_bookings=completed_bookings,
        total_revenue=total_revenue,
        recent_logs=recent_logs,
        pro_filter=pro_filter,
        status_filter=status_filter
    )

@admin_bp.route('/booking/status', methods=['POST'])
@admin_required
def change_booking_status():
    appt_id = request.form.get('appointment_id', type=int)
    new_status = request.form.get('status')
    reason = request.form.get('reason')
    
    user = User.query.filter_by(username='admin').first()
    success, msg = update_booking_status(appt_id, new_status, reason, user)
    
    if success:
        flash(f"Buyurtma holati yangilandi: {new_status}", "success")
    else:
        flash(msg, "error")
        
    return redirect(url_for('admin.dashboard'))

@admin_bp.route('/professionals')
@admin_required
def professionals():
    pros = Professional.query.order_by(Professional.sort_order.asc()).all()
    return render_template('admin/professionals.html', professionals=pros)

@admin_bp.route('/professional/update/<int:pro_id>', methods=['POST'])
@admin_required
def update_professional(pro_id):
    pro = Professional.query.get_or_404(pro_id)
    pro.name = request.form.get('name', pro.name)
    pro.title_uz = request.form.get('title_uz', pro.title_uz)
    pro.specialties_uz = request.form.get('specialties_uz', pro.specialties_uz)
    pro.experience_years = request.form.get('experience_years', pro.experience_years, type=int)
    pro.telegram_chat_id = request.form.get('telegram_chat_id', '').strip()
    pro.sms_phone = request.form.get('sms_phone', '').strip()
    pro.is_active = request.form.get('is_active') == 'on'
    
    db.session.commit()
    flash(f"{pro.name} profili muvaffaqiyatli yangilandi.", "success")
    return redirect(url_for('admin.professionals'))

@admin_bp.route('/services')
@admin_required
def services():
    srvs = Service.query.order_by(Service.sort_order.asc()).all()
    cats = ServiceCategory.query.all()
    return render_template('admin/services.html', services=srvs, categories=cats)

@admin_bp.route('/service/update/<int:service_id>', methods=['POST'])
@admin_required
def update_service(service_id):
    srv = Service.query.get_or_404(service_id)
    srv.name_uz = request.form.get('name_uz', srv.name_uz)
    srv.base_price = request.form.get('base_price', srv.base_price, type=int)
    srv.duration_minutes = request.form.get('duration_minutes', srv.duration_minutes, type=int)
    srv.target_audience = request.form.get('target_audience', srv.target_audience)
    srv.is_active = request.form.get('is_active') == 'on'
    
    db.session.commit()
    flash(f"Xizmat ({srv.name_uz}) yangilandi.", "success")
    return redirect(url_for('admin.services'))

@admin_bp.route('/notifications')
@admin_required
def notifications():
    pros = Professional.query.order_by(Professional.sort_order.asc()).all()
    token_setting = StudioSetting.query.filter_by(key='telegram_bot_token').first()
    bot_token = token_setting.value if token_setting else ''
    
    logs = NotificationLog.query.order_by(NotificationLog.created_at.desc()).limit(30).all()
    return render_template('admin/notifications.html', professionals=pros, bot_token=bot_token, logs=logs)

@admin_bp.route('/notifications/save-bot', methods=['POST'])
@admin_required
def save_bot_token():
    token = request.form.get('telegram_bot_token', '').strip()
    setting = StudioSetting.query.filter_by(key='telegram_bot_token').first()
    if not setting:
        setting = StudioSetting(key='telegram_bot_token', value=token, description='Telegram Bot Token')
        db.session.add(setting)
    else:
        setting.value = token
    db.session.commit()
    flash("Telegram Bot tokeni saqlandi.", "success")
    return redirect(url_for('admin.notifications'))

@admin_bp.route('/notifications/test-pro/<int:pro_id>', methods=['POST'])
@admin_required
def test_pro_notification(pro_id):
    pro = Professional.query.get_or_404(pro_id)
    chat_id = request.form.get('telegram_chat_id', pro.telegram_chat_id)
    if chat_id:
        pro.telegram_chat_id = chat_id.strip()
        db.session.commit()
        
    success, msg = TelegramNotifier.send_test_message(pro.telegram_chat_id, pro.name)
    if success:
        flash(f"{pro.name} uchun test xabari yuborildi!", "success")
    else:
        flash(f"{pro.name} bildirishnoma xatosi: {msg}", "error")
        
    return redirect(url_for('admin.notifications'))

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    if request.method == 'POST':
        # Upload new official logo if provided
        logo_file = request.files.get('logo_file')
        if logo_file and logo_file.filename:
            upload_dir = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_dir, exist_ok=True)
            filename = secure_filename(f"official_logo_{datetime.now().strftime('%Y%m%d%H%M%S')}_{logo_file.filename}")
            filepath = os.path.join(upload_dir, filename)
            logo_file.save(filepath)
            
            logo_s = StudioSetting.query.filter_by(key='brand_logo_path').first()
            if not logo_s:
                logo_s = StudioSetting(key='brand_logo_path', value=f"/static/uploads/{filename}")
                db.session.add(logo_s)
            else:
                logo_s.value = f"/static/uploads/{filename}"
            flash("Yangi rasmiy logotip muvaffaqiyatli yuklandi va o‘rnatildi!", "success")

        # Contact settings
        for k in ['studio_phone', 'studio_address', 'studio_working_hours']:
            val = request.form.get(k)
            if val:
                s = StudioSetting.query.filter_by(key=k).first()
                if not s:
                    db.session.add(StudioSetting(key=k, value=val))
                else:
                    s.value = val
        db.session.commit()
        flash("Studiyaning sozlamalari yangilandi.", "success")
        return redirect(url_for('admin.settings'))

    settings_dict = {s.key: s.value for s in StudioSetting.query.all()}
    return render_template('admin/settings.html', settings=settings_dict)
