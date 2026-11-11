from datetime import date, timedelta
from app.models import db, Professional, Appointment, User
from app.services.booking import create_booking_request

def test_unauthorized_access_redirects_to_login(client):
    # Admin routes
    res_admin = client.get('/admin/dashboard')
    assert res_admin.status_code == 302
    assert '/login' in res_admin.location
    
    # Pro routes
    res_pro = client.get('/pro/dashboard')
    assert res_pro.status_code == 302
    assert '/login' in res_pro.location

def test_admin_login_and_access(client, app):
    # Login as admin
    res = client.post('/login', data={'username': 'admin', 'password': 'Admin2026!WM'}, follow_redirects=True)
    assert res.status_code == 200
    html = res.data.decode('utf-8')
    assert "Administrator Paneli" in html
    
    # Can access admin sections
    res_pros = client.get('/admin/professionals')
    assert res_pros.status_code == 200

def test_professional_data_isolation(client, app):
    with app.app_context():
        pro_akrom = Professional.query.filter_by(slug='akrom').first()
        pro_axror = Professional.query.filter_by(slug='axror').first()
        
        target_date = date.today() + timedelta(days=6)
        if target_date.weekday() in [0, 1]:
            target_date += timedelta(days=2)
            
        # Create an appointment for Axror
        success, appt_axror = create_booking_request(
            professional_id=pro_axror.id,
            service_id=pro_axror.services[0].id,
            appointment_date=target_date,
            start_time_str='14:00',
            end_time_str='15:00',
            customer_name="Axror Mijoz",
            customer_phone="+998909998877"
        )
        assert success is True
        appt_axror_id = appt_axror.id
        
    # Login as Akrom (pro_akrom)
    login_res = client.post('/login', data={'username': 'pro_akrom', 'password': 'Pro2026!WM'}, follow_redirects=True)
    assert login_res.status_code == 200
    akrom_html = login_res.data.decode('utf-8')
    assert "Akrom" in akrom_html
    
    # Verify Akrom's dashboard does NOT show Axror's customer appointment
    assert "Axror Mijoz" not in akrom_html
    
    # Try to illegitimately change status of Axror's appointment as Akrom
    tamper_res = client.post('/pro/booking/status', data={
        'appointment_id': appt_axror_id,
        'status': 'confirmed'
    }, follow_redirects=True)
    assert tamper_res.status_code == 403 or "faqat o'zingizning" in tamper_res.data.decode('utf-8') or "boshqarishingiz mumkin" in tamper_res.data.decode('utf-8')
