from datetime import datetime, date, time, timedelta, timezone
from typing import List, Dict, Tuple, Optional
from flask import current_app
from app.models import db, Professional, WeeklySchedule, ScheduleOverride, Appointment, BookingStatus

def get_business_now() -> datetime:
    """Return current datetime in business timezone (Uzbekistan is UTC+5)."""
    tz = timezone(timedelta(hours=5))
    return datetime.now(tz)

def parse_time_str(time_str: str) -> time:
    """Parse 'HH:MM' string into time object."""
    parts = time_str.strip().split(':')
    return time(int(parts[0]), int(parts[1]))

def format_time_obj(t: time) -> str:
    """Format time object to 'HH:MM'."""
    return f"{t.hour:02d}:{t.minute:02d}"

def add_minutes_to_time(t: time, minutes: int) -> time:
    """Add minutes to a time object, assuming same day."""
    total_minutes = t.hour * 60 + t.minute + minutes
    new_hour = (total_minutes // 60)
    new_minute = total_minutes % 60
    if new_hour >= 24:
        return time(23, 59)
    return time(new_hour, new_minute)

def times_overlap(start_a: time, end_a: time, start_b: time, end_b: time) -> bool:
    """Return True if time intervals [start_a, end_a) and [start_b, end_b) overlap."""
    return max(start_a, start_b) < min(end_a, end_b)

def get_professional_available_slots(
    professional_id: int,
    target_date: date,
    duration_minutes: int,
    slot_interval_minutes: int = 30
) -> List[Dict[str, str]]:
    """
    Generate all bookable time slots for a specific professional on target_date,
    respecting weekly schedules, breaks, overrides/holidays, and existing appointments.
    """
    pro = Professional.query.filter_by(id=professional_id, is_active=True).first()
    if not pro:
        return []
        
    now = get_business_now()
    today = now.date()
    
    # 1. Date Range Validation
    if target_date < today:
        return []
    max_days = current_app.config.get('MAX_BOOKING_ADVANCE_DAYS', 30)
    if target_date > (today + timedelta(days=max_days)):
        return []
        
    # 2. Check Overrides / Holidays first
    override = ScheduleOverride.query.filter_by(
        professional_id=professional_id,
        override_date=target_date
    ).first()
    
    start_time_obj = None
    end_time_obj = None
    break_start_obj = None
    break_end_obj = None
    
    if override:
        if not override.is_available:
            # Blocked holiday / day off
            return []
        if override.start_time and override.end_time:
            start_time_obj = parse_time_str(override.start_time)
            end_time_obj = parse_time_str(override.end_time)
            
    # 3. If no custom hours from override, read WeeklySchedule
    if not start_time_obj:
        weekday = target_date.weekday() # 0 = Monday, 6 = Sunday
        sched = WeeklySchedule.query.filter_by(
            professional_id=professional_id,
            day_of_week=weekday
        ).first()
        
        if not sched or not sched.is_working:
            return []
            
        start_time_obj = parse_time_str(sched.start_time or '09:00')
        end_time_obj = parse_time_str(sched.end_time or '20:00')
        if sched.break_start and sched.break_end:
            break_start_obj = parse_time_str(sched.break_start)
            break_end_obj = parse_time_str(sched.break_end)
            
    # 4. Fetch existing active bookings for this professional on this date
    active_statuses = [
        BookingStatus.PENDING.value,
        BookingStatus.ACCEPTED.value,
        BookingStatus.CONFIRMED.value
    ]
    existing_appointments = Appointment.query.filter(
        Appointment.professional_id == professional_id,
        Appointment.appointment_date == target_date,
        Appointment.status.in_(active_statuses)
    ).all()
    
    booked_intervals = []
    for appt in existing_appointments:
        b_start = parse_time_str(appt.start_time)
        b_end = parse_time_str(appt.end_time)
        booked_intervals.append((b_start, b_end))
        
    # 5. Generate candidate slots
    buffer_mins = current_app.config.get('APPOINTMENT_BUFFER_MINUTES', 0)
    total_slot_needed = duration_minutes + buffer_mins
    
    available_slots = []
    current_cursor = start_time_obj
    min_notice_hours = current_app.config.get('MIN_BOOKING_NOTICE_HOURS', 2)
    min_booking_time = now + timedelta(hours=min_notice_hours)
    
    while True:
        slot_end = add_minutes_to_time(current_cursor, duration_minutes)
        slot_end_with_buffer = add_minutes_to_time(current_cursor, total_slot_needed)
        
        # Check if slot extends beyond working hours
        if slot_end > end_time_obj:
            break
            
        # Check notice window if booking is for today
        if target_date == today:
            slot_dt = datetime.combine(target_date, current_cursor, tzinfo=now.tzinfo)
            if slot_dt < min_booking_time:
                # Slot is too soon
                current_cursor = add_minutes_to_time(current_cursor, slot_interval_minutes)
                continue
                
        # Check collision with break
        collision = False
        if break_start_obj and break_end_obj:
            if times_overlap(current_cursor, slot_end, break_start_obj, break_end_obj):
                collision = True
                
        # Check collision with existing bookings
        if not collision:
            for b_start, b_end in booked_intervals:
                if times_overlap(current_cursor, slot_end_with_buffer, b_start, b_end):
                    collision = True
                    break
                    
        if not collision:
            available_slots.append({
                'start_time': format_time_obj(current_cursor),
                'end_time': format_time_obj(slot_end),
                'label': f"{format_time_obj(current_cursor)} – {format_time_obj(slot_end)}"
            })
            
        # Advance cursor
        next_cursor = add_minutes_to_time(current_cursor, slot_interval_minutes)
        if next_cursor <= current_cursor or next_cursor >= end_time_obj:
            break
        current_cursor = next_cursor
        
    return available_slots

def validate_and_lock_slot(
    professional_id: int,
    target_date: date,
    start_time_str: str,
    end_time_str: str,
    exclude_appointment_id: Optional[int] = None
) -> Tuple[bool, str]:
    """
    Strict server-side validation during transaction to prevent double bookings.
    Returns (True, "") or (False, "Reason for conflict").
    """
    req_start = parse_time_str(start_time_str)
    req_end = parse_time_str(end_time_str)
    
    # 1. Check working hours & overrides
    weekday = target_date.weekday()
    override = ScheduleOverride.query.filter_by(
        professional_id=professional_id,
        override_date=target_date
    ).first()
    
    if override and not override.is_available:
        return False, "Mutaxassis ushbu kunda dam olish kunini belgilagan."
        
    sched = WeeklySchedule.query.filter_by(
        professional_id=professional_id,
        day_of_week=weekday
    ).first()
    
    if not sched or not sched.is_working:
        return False, "Mutaxassis haftaning bu kunida ishlamaydi."
        
    work_start = parse_time_str(sched.start_time)
    work_end = parse_time_str(sched.end_time)
    
    if req_start < work_start or req_end > work_end:
        return False, "Tanlangan vaqt mutaxassisning ish soatlaridan tashqarida."
        
    if sched.break_start and sched.break_end:
        b_start = parse_time_str(sched.break_start)
        b_end = parse_time_str(sched.break_end)
        if times_overlap(req_start, req_end, b_start, b_end):
            return False, "Tanlangan vaqt mutaxassisning tushlik tanaffusiga to‘g‘ri keladi."
            
    # 2. Check for overlapping active appointments
    active_statuses = [
        BookingStatus.PENDING.value,
        BookingStatus.ACCEPTED.value,
        BookingStatus.CONFIRMED.value
    ]
    query = Appointment.query.filter(
        Appointment.professional_id == professional_id,
        Appointment.appointment_date == target_date,
        Appointment.status.in_(active_statuses)
    )
    if exclude_appointment_id:
        query = query.filter(Appointment.id != exclude_appointment_id)
        
    existing = query.all()
    for appt in existing:
        ex_start = parse_time_str(appt.start_time)
        ex_end = parse_time_str(appt.end_time)
        if times_overlap(req_start, req_end, ex_start, ex_end):
            return False, "Kechirasiz, bu vaqt oraliq hozirgina boshqa mijoz tomonidan band qilindi."
            
    return True, ""
