import secrets
import string
from datetime import datetime, date
from typing import Optional, Dict, Any, Tuple
from flask import current_app
from app.models import db, Appointment, Professional, Service, User, BookingStatus
from app.services.availability import validate_and_lock_slot, parse_time_str
from app.services.notifications import dispatch_appointment_alerts

def generate_booking_reference() -> str:
    """Generate a unique reference code, e.g. WM-2026-X8B2K."""
    alphabet = string.ascii_uppercase + "23456789" # Avoid ambiguous 0/O, 1/I
    suffix = ''.join(secrets.choice(alphabet) for _ in range(5))
    year = datetime.now().year
    return f"WM-{year}-{suffix}"

def create_booking_request(
    professional_id: int,
    service_id: int,
    appointment_date: date,
    start_time_str: str,
    end_time_str: str,
    customer_name: str,
    customer_phone: str,
    customer_email: Optional[str] = None,
    customer_note: Optional[str] = None,
    customer_id: Optional[int] = None
) -> Tuple[bool, Any]:
    """
    Safely creates a new booking request with transaction concurrency validation.
    Returns: (success: bool, appointment_or_error_message: Any)
    """
    # 1. Basic validation
    pro = Professional.query.filter_by(id=professional_id, is_active=True).first()
    if not pro:
        return False, "Tanlangan mutaxassis topilmadi yoki faol emas."
        
    srv = Service.query.filter_by(id=service_id, is_active=True).first()
    if not srv:
        return False, "Tanlangan xizmat topilmadi yoki faol emas."
        
    if not customer_name or len(customer_name.strip()) < 2:
        return False, "Iltimos, ismingizni to‘liq kiriting."
        
    if not customer_phone or len(customer_phone.strip()) < 7:
        return False, "Iltimos, to‘g‘ri telefon raqamini kiriting."
        
    # 2. Concurrency Check & Slot Validation
    is_valid, error_msg = validate_and_lock_slot(
        professional_id=professional_id,
        target_date=appointment_date,
        start_time_str=start_time_str,
        end_time_str=end_time_str
    )
    if not is_valid:
        return False, error_msg
        
    # 3. Calculate price and duration (allowing professional custom override if defined)
    price = srv.base_price
    duration = srv.duration_minutes
    
    # Check custom price/duration from junction table
    custom_row = db.session.execute(
        db.select(db.text("custom_price, custom_duration FROM professional_services WHERE professional_id = :p AND service_id = :s"))
        .params(p=professional_id, s=service_id)
    ).first()
    if custom_row:
        if custom_row[0]:
            price = custom_row[0]
        if custom_row[1]:
            duration = custom_row[1]
            
    # Determine initial status (manual approval vs auto confirmation)
    manual_approval = current_app.config.get('MANUAL_APPROVAL_REQUIRED', False)
    initial_status = BookingStatus.PENDING.value if manual_approval else BookingStatus.CONFIRMED.value
    
    # 4. Create record under transaction
    ref_code = generate_booking_reference()
    while Appointment.query.filter_by(reference_code=ref_code).first():
        ref_code = generate_booking_reference()
        
    try:
        appointment = Appointment(
            reference_code=ref_code,
            professional_id=professional_id,
            service_id=service_id,
            customer_id=customer_id,
            customer_name=customer_name.strip(),
            customer_phone=customer_phone.strip(),
            customer_email=customer_email.strip() if customer_email else None,
            customer_note=customer_note.strip() if customer_note else None,
            appointment_date=appointment_date,
            start_time=start_time_str,
            end_time=end_time_str,
            duration_minutes=duration,
            price=price,
            status=initial_status
        )
        db.session.add(appointment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return False, f"Ma'lumotlar bazasida xatolik: {str(e)}"
        
    # 5. Dispatch notification to the assigned professional
    try:
        dispatch_appointment_alerts(appointment)
    except Exception as e:
        current_app.logger.error(f"Notification error for {ref_code}: {e}")
        
    return True, appointment

def update_booking_status(
    appointment_id: int,
    new_status: str,
    reason: Optional[str] = None,
    acting_user: Optional[User] = None
) -> Tuple[bool, str]:
    """
    Transition booking status with state-machine and role permission validation.
    """
    appt = Appointment.query.get(appointment_id)
    if not appt:
        return False, "Buyurtma topilmadi."
        
    # Role permissions check
    if acting_user:
        if acting_user.role == 'professional':
            # Must own the appointment
            if not acting_user.professional or acting_user.professional.id != appt.professional_id:
                return False, "Siz faqat o‘zingizga tegishli buyurtmalarni boshqarishingiz mumkin."
        elif acting_user.role == 'customer':
            # Customer can only cancel their own pending/confirmed appointment
            if appt.customer_id != acting_user.id:
                return False, "Ruxsat etilmagan amal."
            if new_status != BookingStatus.CANCELLED.value:
                return False, "Mijoz faqat buyurtmani bekor qilishi mumkin."
                
    valid_transitions = {
        BookingStatus.PENDING.value: [
            BookingStatus.ACCEPTED.value,
            BookingStatus.CONFIRMED.value,
            BookingStatus.REJECTED.value,
            BookingStatus.CANCELLED.value
        ],
        BookingStatus.ACCEPTED.value: [
            BookingStatus.CONFIRMED.value,
            BookingStatus.CANCELLED.value,
            BookingStatus.REJECTED.value
        ],
        BookingStatus.CONFIRMED.value: [
            BookingStatus.COMPLETED.value,
            BookingStatus.CANCELLED.value,
            BookingStatus.NO_SHOW.value
        ],
        BookingStatus.COMPLETED.value: [],
        BookingStatus.CANCELLED.value: [],
        BookingStatus.REJECTED.value: [],
        BookingStatus.NO_SHOW.value: []
    }
    
    current_s = appt.status
    if new_status not in valid_transitions.get(current_s, []):
        return False, f"'{current_s}' holatidan '{new_status}' holatiga o‘tish mumkin emas."
        
    appt.status = new_status
    if new_status == BookingStatus.REJECTED.value and reason:
        appt.rejection_reason = reason
    elif new_status == BookingStatus.CANCELLED.value and reason:
        appt.cancellation_reason = reason
        
    db.session.commit()
    return True, "Holat muvaffaqiyatli yangilandi."
