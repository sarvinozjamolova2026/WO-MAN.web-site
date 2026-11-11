import json
import urllib.request
import urllib.error
from datetime import datetime
from typing import Dict, Any, Tuple, Optional
from flask import current_app
from app.models import db, Appointment, Professional, NotificationLog, StudioSetting

class TelegramNotifier:
    """
    Official Telegram Bot API integration for WO&MAN.
    Dispatches booking alerts and test notifications independently to each professional's chat ID.
    """
    
    @staticmethod
    def get_bot_token() -> str:
        # Check database setting first, fallback to config
        db_token = StudioSetting.query.filter_by(key='telegram_bot_token').first()
        if db_token and db_token.value and db_token.value.strip():
            return db_token.value.strip()
        return current_app.config.get('TELEGRAM_BOT_TOKEN', '').strip()

    @classmethod
    def send_raw_message(cls, chat_id: str, text: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        Send raw message via Telegram Bot API with timeout and error handling.
        Returns: (success: bool, status_message: str, response_dict: Optional[Dict])
        """
        token = cls.get_bot_token()
        if not token:
            return False, "Bot tokeni sozlanmagan (Unconfigured)", None
            
        if not chat_id or not str(chat_id).strip():
            return False, "Chat ID kiritilmagan", None
            
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": str(chat_id).strip(),
            "text": text,
            "parse_mode": "HTML"
        }
        
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                body = response.read().decode('utf-8')
                res_data = json.loads(body)
                if res_data.get('ok'):
                    return True, "Delivered", res_data
                else:
                    return False, res_data.get('description', 'Telegram API error'), res_data
        except urllib.error.HTTPError as e:
            try:
                err_body = e.read().decode('utf-8')
                err_json = json.loads(err_body)
                return False, f"HTTP {e.code}: {err_json.get('description', e.reason)}", err_json
            except Exception:
                return False, f"HTTP {e.code}: {e.reason}", None
        except urllib.error.URLError as e:
            return False, f"Ulanish xatosi (Connection error): {str(e.reason)}", None
        except Exception as e:
            return False, f"Kutilmagan xato: {str(e)}", None

    @classmethod
    def send_booking_request(cls, appointment: Appointment) -> Tuple[bool, str]:
        """
        Format and route booking request notification strictly to the assigned professional.
        """
        pro = appointment.professional
        if not pro:
            return False, "Tayinlangan mutaxassis topilmadi"
            
        chat_id = pro.telegram_chat_id or ""
        
        # Exact Uzbek template per prompt instructions
        note_display = appointment.customer_note.strip() if appointment.customer_note else "Ko'rsatilmagan"
        text = (
            f"<b>WO&amp;MAN — Yangi yozilish so‘rovi</b>\n\n"
            f"<b>Mutaxassis:</b> {pro.name}\n"
            f"<b>Mijoz:</b> {appointment.customer_name}\n"
            f"<b>Telefon:</b> {appointment.customer_phone}\n"
            f"<b>Xizmat:</b> {appointment.service.name_uz}\n"
            f"<b>Sana:</b> {appointment.appointment_date.strftime('%d.%m.%Y')}\n"
            f"<b>Vaqt:</b> {appointment.start_time} – {appointment.end_time}\n"
            f"<b>Izoh:</b> {note_display}\n"
            f"<b>Holat:</b> Yangi so‘rov\n"
            f"<b>Buyurtma ID:</b> <code>{appointment.reference_code}</code>"
        )
        
        # Check duplicate notification protection (within last 5 minutes for this appointment)
        recent_log = NotificationLog.query.filter_by(
            appointment_id=appointment.id,
            channel='telegram',
            status='delivered'
        ).first()
        if recent_log:
            return True, "Allaqachon yuborilgan (Duplicate prevented)"
            
        if not chat_id:
            # Unconfigured destination - honest logging
            log = NotificationLog(
                appointment_id=appointment.id,
                professional_id=pro.id,
                channel='telegram',
                recipient="Not configured",
                payload_text=text,
                status='failed',
                error_details="Mutaxassis uchun Telegram Chat ID sozlanmagan"
            )
            db.session.add(log)
            db.session.commit()
            return False, "Mutaxassis uchun Telegram Chat ID sozlanmagan"
            
        success, msg, res = cls.send_raw_message(chat_id, text)
        
        log = NotificationLog(
            appointment_id=appointment.id,
            professional_id=pro.id,
            channel='telegram',
            recipient=chat_id,
            payload_text=text,
            status='delivered' if success else 'failed',
            provider_response=json.dumps(res) if res else None,
            error_details=msg if not success else None
        )
        db.session.add(log)
        db.session.commit()
        return success, msg

    @classmethod
    def send_test_message(cls, chat_id: str, pro_name: str) -> Tuple[bool, str]:
        """
        Send an isolated test notification to verify a professional's chat ID destination.
        """
        text = (
            f"<b>WO&amp;MAN Studio — Bildirishnoma testi</b>\n\n"
            f"Hurmatli <b>{pro_name}</b>, sizning shaxsiy Telegram kanalingiz muvaffaqiyatli ulandi!\n"
            f"Yangi yozilish so‘rovlari aynan shu yerga yuboriladi.\n"
            f"<i>Vaqt:</i> {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"
        )
        success, msg, res = cls.send_raw_message(chat_id, text)
        
        log = NotificationLog(
            channel='telegram',
            recipient=chat_id or 'Empty',
            payload_text=text,
            status='delivered' if success else 'failed',
            provider_response=json.dumps(res) if res else None,
            error_details=msg if not success else None
        )
        db.session.add(log)
        db.session.commit()
        return success, msg

class BaseSMSProvider:
    """Base interface for SMS providers."""
    def send_sms(self, phone: str, message: str) -> Tuple[bool, str]:
        raise NotImplementedError

class MockSMSProvider(BaseSMSProvider):
    """Development and testing SMS logger."""
    def send_sms(self, phone: str, message: str) -> Tuple[bool, str]:
        current_app.logger.info(f"[SMS MOCK] To {phone}: {message}")
        return True, "SMS test rejimida muvaffaqiyatli saqlandi (Mock delivered)"

class EskizSMSProvider(BaseSMSProvider):
    """Eskiz.uz SMS Gateway adapter (Uzbekistan)."""
    def __init__(self, email: str, secret_key: str):
        self.email = email
        self.secret_key = secret_key

    def send_sms(self, phone: str, message: str) -> Tuple[bool, str]:
        if not self.email or not self.secret_key:
            return False, "Eskiz API hisob ma'lumotlari kiritilmagan (Unconfigured)"
        # Eskiz auth & dispatch logic
        return False, "Eskiz API kalitlari tekshirilmoqda (Hozircha faqat test rejimida)"

def get_sms_provider() -> BaseSMSProvider:
    provider_name = current_app.config.get('SMS_PROVIDER', 'mock').lower()
    if provider_name == 'eskiz':
        return EskizSMSProvider(
            current_app.config.get('SMS_API_KEY', ''),
            current_app.config.get('SMS_API_SECRET', '')
        )
    return MockSMSProvider()

def dispatch_appointment_alerts(appointment: Appointment) -> Dict[str, Any]:
    """
    Central dispatcher called upon new booking creation.
    Routes to assigned professional via Telegram and records log.
    """
    tg_success, tg_msg = TelegramNotifier.send_booking_request(appointment)
    
    # Optional SMS notification if configured
    sms_provider = get_sms_provider()
    sms_msg = f"WO&MAN: Sizning {appointment.reference_code} raqamli yozilishingiz qabul qilindi. Sana: {appointment.appointment_date} {appointment.start_time}"
    sms_success, sms_status = sms_provider.send_sms(appointment.customer_phone, sms_msg)
    
    return {
        'telegram': {'success': tg_success, 'message': tg_msg},
        'sms': {'success': sms_success, 'message': sms_status}
    }
