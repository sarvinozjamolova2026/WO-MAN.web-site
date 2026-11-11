from datetime import date, timedelta
from app.models import db, Professional, Service, Appointment, NotificationLog
from app.services.booking import create_booking_request
from app.services.notifications import TelegramNotifier

def test_independent_notification_routing_to_assigned_pro(app):
    with app.app_context():
        # Assign distinct Chat IDs to two different barbers
        pro_akrom = Professional.query.filter_by(slug='akrom').first()
        pro_axror = Professional.query.filter_by(slug='axror').first()
        
        pro_akrom.telegram_chat_id = "111111111"
        pro_axror.telegram_chat_id = "222222222"
        db.session.commit()
        
        target_date = date.today() + timedelta(days=5)
        if target_date.weekday() in [0, 1]:
            target_date += timedelta(days=2)
            
        # Book Akrom
        srv_akrom = pro_akrom.services[0]
        success, appt_akrom = create_booking_request(
            professional_id=pro_akrom.id,
            service_id=srv_akrom.id,
            appointment_date=target_date,
            start_time_str='10:00',
            end_time_str='10:35',
            customer_name="Akrom Mijoz",
            customer_phone="+998901112233",
            customer_note="Fade toza bo'lsin"
        )
        assert success is True
        
        # Check notification logs for this appointment
        logs = NotificationLog.query.filter_by(appointment_id=appt_akrom.id).all()
        assert len(logs) > 0
        
        # Verify routing destination is ONLY pro_akrom's chat ID (111111111) and NOT pro_axror's (222222222)
        recipients = [l.recipient for l in logs]
        assert "111111111" in recipients
        assert "222222222" not in recipients
        
        # Verify Uzbek template contains essential fields
        log_text = logs[0].payload_text
        assert "WO&amp;MAN — Yangi yozilish so‘rovi" in log_text or "WO&MAN" in log_text
        assert f"Mutaxassis:</b> {pro_akrom.name}" in log_text or pro_akrom.name in log_text
        assert "Akrom Mijoz" in log_text
        assert "+998901112233" in log_text
        assert "Fade toza bo'lsin" in log_text
        assert appt_akrom.reference_code in log_text
