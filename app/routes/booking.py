from datetime import datetime, date
from flask import Blueprint, render_template, request, jsonify, Response, current_app, session
from app.models import db, Professional, Service, Appointment, BookingStatus
from app.services.availability import get_professional_available_slots, parse_time_str
from app.services.booking import create_booking_request

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/book')
def book_page():
    pro_slug = request.args.get('pro')
    service_slug = request.args.get('service')
    
    preselect_pro = None
    if pro_slug:
        preselect_pro = Professional.query.filter_by(slug=pro_slug, is_active=True).first()
        
    preselect_service = None
    if service_slug:
        preselect_service = Service.query.filter_by(slug=service_slug, is_active=True).first()
        
    professionals = Professional.query.filter_by(is_active=True).order_by(Professional.sort_order.asc()).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.sort_order.asc()).all()
    
    return render_template(
        'book.html',
        professionals=professionals,
        services=services,
        preselect_pro=preselect_pro,
        preselect_service=preselect_service
    )

@booking_bp.route('/booking/confirmation/<reference_code>')
def booking_confirmation(reference_code):
    appointment = Appointment.query.filter_by(reference_code=reference_code).first_or_404()
    return render_template('booking_confirmation.html', appt=appointment)

@booking_bp.route('/api/availability')
def api_availability():
    pro_id = request.args.get('pro_id', type=int)
    service_id = request.args.get('service_id', type=int)
    date_str = request.args.get('date')
    
    if not pro_id or not service_id or not date_str:
        return jsonify({'error': "Kerakli parametrlar (pro_id, service_id, date) yetarli emas"}), 400
        
    try:
        target_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({'error': "Noto'g'ri sana formati (YYYY-MM-DD kutilmoqda)"}), 400
        
    srv = Service.query.get(service_id)
    if not srv:
        return jsonify({'error': "Xizmat topilmadi"}), 404
        
    slots = get_professional_available_slots(
        professional_id=pro_id,
        target_date=target_date,
        duration_minutes=srv.duration_minutes
    )
    return jsonify({'slots': slots, 'count': len(slots)})

@booking_bp.route('/api/booking/create', methods=['POST'])
def api_create_booking():
    data = request.get_json() or {}
    
    try:
        pro_id = int(data.get('professional_id'))
        srv_id = int(data.get('service_id'))
        appt_date = datetime.strptime(data.get('appointment_date'), '%Y-%m-%d').date()
        start_time = str(data.get('start_time')).strip()
        end_time = str(data.get('end_time')).strip()
        name = str(data.get('customer_name', '')).strip()
        phone = str(data.get('customer_phone', '')).strip()
        email = data.get('customer_email')
        note = data.get('customer_note')
        customer_id = session.get('user_id')
    except (ValueError, TypeError) as e:
        return jsonify({'success': False, 'message': f"Ma'lumotlar formati noto'g'ri: {str(e)}"}), 400
        
    success, result = create_booking_request(
        professional_id=pro_id,
        service_id=srv_id,
        appointment_date=appt_date,
        start_time_str=start_time,
        end_time_str=end_time,
        customer_name=name,
        customer_phone=phone,
        customer_email=email,
        customer_note=note,
        customer_id=customer_id
    )
    
    if not success:
        # Check if error was slot collision
        status_code = 409 if "hozirgina boshqa mijoz" in result or "dam olish" in result or "ishlamaydi" in result else 400
        return jsonify({'success': False, 'message': result}), status_code
        
    return jsonify({
        'success': True,
        'reference_code': result.reference_code,
        'status': result.status,
        'message': "Yozilish so‘rovi muvaffaqiyatli qabul qilindi!"
    }), 201

@booking_bp.route('/booking/download-ics/<reference_code>')
def download_ics(reference_code):
    appt = Appointment.query.filter_by(reference_code=reference_code).first_or_404()
    
    # Format iCalendar
    date_str = appt.appointment_date.strftime('%Y%m%d')
    start_clean = appt.start_time.replace(':', '') + '00'
    end_clean = appt.end_time.replace(':', '') + '00'
    now_clean = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    
    ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//WO&MAN//Beauty & Grooming Studio//UZ
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{appt.reference_code}@woandman.uz
DTSTAMP:{now_clean}
DTSTART;TZID=Asia/Tashkent:{date_str}T{start_clean}
DTEND;TZID=Asia/Tashkent:{date_str}T{end_clean}
SUMMARY:WO&MAN — {appt.service.name_uz} ({appt.professional.name})
DESCRIPTION:Buyurtma kodi: {appt.reference_code}\\nMutaxassis: {appt.professional.name}\\nXizmat: {appt.service.name_uz}\\nTelefon: +998 71 200 00 20
LOCATION:Amir Temur shox ko'chasi 45, Toshkent
STATUS:CONFIRMED
END:VEVENT
END:VCALENDAR"""

    return Response(
        ics_content,
        mimetype="text/calendar",
        headers={"Content-Disposition": f"attachment; filename=wo_and_man_{appt.reference_code}.ics"}
    )
