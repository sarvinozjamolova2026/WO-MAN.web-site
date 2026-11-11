from datetime import date, timedelta
from app.models import Professional, Service, Appointment
from app.services.availability import get_professional_available_slots, parse_time_str
from app.services.booking import create_booking_request

def test_availability_slot_generation(app):
    with app.app_context():
        pro = Professional.query.filter_by(slug='akrom').first()
        srv = pro.services[0]
        
        # Pick a target date (e.g. Wednesday or Thursday - Akrom works every day except Monday)
        tomorrow = date.today() + timedelta(days=2)
        if tomorrow.weekday() == 0: # Monday is day-off for Akrom in seed
            tomorrow += timedelta(days=1)
            
        slots = get_professional_available_slots(
            professional_id=pro.id,
            target_date=tomorrow,
            duration_minutes=srv.duration_minutes
        )
        
        assert len(slots) > 0, "Expected available slots for active professional on working day"
        
        # Verify no slot overlaps with 13:00 - 14:00 (lunch break)
        for s in slots:
            start_t = parse_time_str(s['start_time'])
            end_t = parse_time_str(s['end_time'])
            assert not (start_t < parse_time_str('14:00') and end_t > parse_time_str('13:00')), \
                f"Slot {s['label']} overlaps with lunch break 13:00-14:00"

def test_booking_creation_and_concurrency_prevention(app):
    with app.app_context():
        pro = Professional.query.filter_by(slug='akrom').first()
        srv = pro.services[0]
        
        booking_date = date.today() + timedelta(days=3)
        if booking_date.weekday() == 0:
            booking_date += timedelta(days=1)
            
        # 1. First booking attempt -> should succeed
        success, appt = create_booking_request(
            professional_id=pro.id,
            service_id=srv.id,
            appointment_date=booking_date,
            start_time_str='11:00',
            end_time_str='11:35',
            customer_name="Test Mijoz",
            customer_phone="+998901234567",
            customer_email="test@woandman.uz",
            customer_note="Qisqa qilib oling"
        )
        assert success is True
        assert appt is not None
        assert appt.reference_code.startswith("WM-")
        
        # 2. Overlapping booking attempt for the exact same slot -> MUST be blocked
        success_overlap, overlap_result = create_booking_request(
            professional_id=pro.id,
            service_id=srv.id,
            appointment_date=booking_date,
            start_time_str='11:15',  # Overlaps with 11:00 - 11:35
            end_time_str='11:50',
            customer_name="Boshqa Mijoz",
            customer_phone="+998909876543"
        )
        assert success_overlap is False
        assert "hozirgina boshqa mijoz" in overlap_result or "band qilindi" in overlap_result

def test_api_booking_endpoint_returns_409_on_conflict(client, app):
    with app.app_context():
        pro = Professional.query.filter_by(slug='axror').first()
        srv = pro.services[0]
        
        booking_date = date.today() + timedelta(days=4)
        if booking_date.weekday() == 1: # Tuesday is day-off for Axror
            booking_date += timedelta(days=1)
        booking_date_str = booking_date.strftime('%Y-%m-%d')
        
        payload = {
            'professional_id': pro.id,
            'service_id': srv.id,
            'appointment_date': booking_date_str,
            'start_time': '15:00',
            'end_time': '16:00',
            'customer_name': 'Ziyoda Karimova',
            'customer_phone': '+998901112233'
        }
        
        # First booking succeeds with 201 Created
        res1 = client.post('/api/booking/create', json=payload)
        assert res1.status_code == 201
        data1 = res1.get_json()
        assert data1['success'] is True
        assert 'WM-' in data1['reference_code']
        
        # Second identical booking rejected with 409 Conflict
        res2 = client.post('/api/booking/create', json=payload)
        assert res2.status_code == 409
        data2 = res2.get_json()
        assert data2['success'] is False
