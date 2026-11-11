import os
from datetime import datetime, date
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from app.models import (
    db, Professional, Appointment, WeeklySchedule, ScheduleOverride,
    PortfolioItem, BookingStatus
)
from app.routes.auth import pro_required
from app.services.booking import update_booking_status
from app.services.notifications import TelegramNotifier

pro_bp = Blueprint('pro', __name__, url_prefix='/pro')

@pro_bp.route('/dashboard')
@pro_required
def dashboard():
    pro_id = session.get('pro_id')
    pro = Professional.query.get_or_404(pro_id)
    
    # Strictly isolated: only appointments for this specific professional
    appointments = pro.appointments.order_by(Appointment.appointment_date.desc(), Appointment.start_time.asc()).all()
    schedules = pro.schedules.order_by(WeeklySchedule.day_of_week.asc()).all()
    overrides = pro.overrides.order_by(ScheduleOverride.override_date.asc()).all()
    portfolio = pro.portfolio_items.order_by(PortfolioItem.sort_order.asc()).all()
    
    today = date.today()
    today_appts = [a for a in appointments if a.appointment_date == today and a.status in ['confirmed', 'accepted', 'pending']]
    pending_appts = [a for a in appointments if a.status == 'pending']
    
    return render_template(
        'pro/dashboard.html',
        pro=pro,
        appointments=appointments,
        today_appts=today_appts,
        pending_appts=pending_appts,
        schedules=schedules,
        overrides=overrides,
        portfolio=portfolio
    )

@pro_bp.route('/booking/status', methods=['POST'])
@pro_required
def change_status():
    pro_id = session.get('pro_id')
    appt_id = request.form.get('appointment_id', type=int)
    new_status = request.form.get('status')
    reason = request.form.get('reason')
    
    appt = Appointment.query.get_or_404(appt_id)
    if appt.professional_id != pro_id:
        flash("Siz faqat o'zingizning buyurtmalaringizni boshqarishingiz mumkin.", "error")
        return redirect(url_for('pro.dashboard'))
        
    user = db.session.get(db.Model._decl_class_registry['User'], session.get('user_id'))
    success, msg = update_booking_status(appt_id, new_status, reason, user)
    
    if success:
        flash(f"Buyurtma holati yangilandi: {new_status}", "success")
    else:
        flash(msg, "error")
        
    return redirect(url_for('pro.dashboard'))

@pro_bp.route('/schedule/update', methods=['POST'])
@pro_required
def update_schedule():
    pro_id = session.get('pro_id')
    pro = Professional.query.get_or_404(pro_id)
    
    for sched in pro.schedules:
        is_working = request.form.get(f'working_{sched.day_of_week}') == 'on'
        start_time = request.form.get(f'start_{sched.day_of_week}', '09:00')
        end_time = request.form.get(f'end_{sched.day_of_week}', '20:00')
        break_start = request.form.get(f'break_start_{sched.day_of_week}', '13:00')
        break_end = request.form.get(f'break_end_{sched.day_of_week}', '14:00')
        
        sched.is_working = is_working
        sched.start_time = start_time
        sched.end_time = end_time
        sched.break_start = break_start
        sched.break_end = break_end
        
    db.session.commit()
    flash("Ish jadvali muvaffaqiyatli saqlandi.", "success")
    return redirect(url_for('pro.dashboard'))

@pro_bp.route('/override/add', methods=['POST'])
@pro_required
def add_override():
    pro_id = session.get('pro_id')
    date_str = request.form.get('override_date')
    reason = request.form.get('reason', '')
    is_avail = request.form.get('is_available') == 'on'
    
    if date_str:
        ov_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        ov = ScheduleOverride(
            professional_id=pro_id,
            override_date=ov_date,
            is_available=is_avail,
            reason=reason
        )
        db.session.add(ov)
        db.session.commit()
        flash(f"{date_str} sanasi uchun jadval istisnosi kiritildi.", "success")
        
    return redirect(url_for('pro.dashboard'))

@pro_bp.route('/override/delete/<int:override_id>', methods=['POST'])
@pro_required
def delete_override(override_id):
    pro_id = session.get('pro_id')
    ov = ScheduleOverride.query.filter_by(id=override_id, professional_id=pro_id).first_or_404()
    db.session.delete(ov)
    db.session.commit()
    flash("Istisno o‘chirildi.", "success")
    return redirect(url_for('pro.dashboard'))

@pro_bp.route('/portfolio/add', methods=['POST'])
@pro_required
def add_portfolio_item():
    pro_id = session.get('pro_id')
    title_uz = request.form.get('title_uz', 'Yangi ish')
    category = request.form.get('category', 'styling')
    
    image_file = request.files.get('image')
    before_file = request.files.get('before_image')
    
    image_url = '/static/images/portfolio/work-1-after.svg' # Fallback
    before_url = None
    
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    
    if image_file and image_file.filename:
        filename = secure_filename(f"pro_{pro_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{image_file.filename}")
        image_file.save(os.path.join(upload_dir, filename))
        image_url = f"/static/uploads/{filename}"
        
    if before_file and before_file.filename:
        b_filename = secure_filename(f"pro_{pro_id}_before_{datetime.now().strftime('%Y%m%d%H%M%S')}_{before_file.filename}")
        before_file.save(os.path.join(upload_dir, b_filename))
        before_url = f"/static/uploads/{b_filename}"
        
    item = PortfolioItem(
        professional_id=pro_id,
        title_uz=title_uz,
        title_ru=title_uz,
        title_en=title_uz,
        category=category,
        image_url=image_url,
        before_image_url=before_url,
        is_approved=True,
        is_featured=True
    )
    db.session.add(item)
    db.session.commit()
    flash("Yangi portfolio ishi muvaffaqiyatli yuklandi.", "success")
    return redirect(url_for('pro.dashboard'))

@pro_bp.route('/portfolio/delete/<int:item_id>', methods=['POST'])
@pro_required
def delete_portfolio_item(item_id):
    pro_id = session.get('pro_id')
    item = PortfolioItem.query.filter_by(id=item_id, professional_id=pro_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash("Portfolio ishi o‘chirildi.", "success")
    return redirect(url_for('pro.dashboard'))

@pro_bp.route('/test-telegram', methods=['POST'])
@pro_required
def test_telegram():
    pro_id = session.get('pro_id')
    pro = Professional.query.get_or_404(pro_id)
    chat_id = request.form.get('telegram_chat_id', pro.telegram_chat_id)
    
    if chat_id != pro.telegram_chat_id:
        pro.telegram_chat_id = chat_id
        db.session.commit()
        
    success, msg = TelegramNotifier.send_test_message(chat_id, pro.name)
    if success:
        flash("Test xabari Telegram'ingizga yuborildi!", "success")
    else:
        flash(f"Telegram testi muvaffaqiyatsiz bo'ldi: {msg}", "error")
        
    return redirect(url_for('pro.dashboard'))

@pro_bp.route('/profile/update', methods=['POST'])
@pro_required
def update_profile():
    pro_id = session.get('pro_id')
    pro = Professional.query.get_or_404(pro_id)
    
    pro.name = request.form.get('name', pro.name).strip()
    pro.title_uz = request.form.get('title_uz', pro.title_uz).strip()
    pro.bio_uz = request.form.get('bio_uz', pro.bio_uz).strip()
    pro.specialties_uz = request.form.get('specialties_uz', pro.specialties_uz).strip()
    pro.skills_uz = request.form.get('skills_uz', pro.skills_uz).strip()
    pro.sms_phone = request.form.get('sms_phone', pro.sms_phone).strip()
    pro.instagram_url = request.form.get('instagram_url', pro.instagram_url).strip()
    
    exp = request.form.get('experience_years')
    if exp:
        try:
            pro.experience_years = int(exp)
        except ValueError:
            pass
            
    photo_file = request.files.get('photo')
    if photo_file and photo_file.filename:
        upload_dir = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        filename = secure_filename(f"pro_{pro.id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{photo_file.filename}")
        photo_file.save(os.path.join(upload_dir, filename))
        pro.photo_url = f"/static/uploads/{filename}"
        
    db.session.commit()
    flash("Siz haqingizdagi ma'lumotlar muvaffaqiyatli yangilandi!", "success")
    return redirect(url_for('pro.dashboard'))
