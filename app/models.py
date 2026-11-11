import enum
from datetime import datetime, date, time
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class RoleEnum(str, enum.Enum):
    ADMIN = 'admin'
    PROFESSIONAL = 'professional'
    CUSTOMER = 'customer'

class BookingStatus(str, enum.Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    CONFIRMED = 'confirmed'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    NO_SHOW = 'no_show'
    REJECTED = 'rejected'

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(30), nullable=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default=RoleEnum.CUSTOMER.value, nullable=False)
    full_name = db.Column(db.String(120), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    professional = db.relationship('Professional', backref='user', uselist=False, cascade='all, delete-orphan')
    appointments = db.relationship('Appointment', backref='customer', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def is_admin(self) -> bool:
        return self.role == RoleEnum.ADMIN.value

    def is_pro(self) -> bool:
        return self.role == RoleEnum.PROFESSIONAL.value

# Many-to-many relationship table between Professional and Service
professional_services = db.Table(
    'professional_services',
    db.Column('professional_id', db.Integer, db.ForeignKey('professionals.id', ondelete='CASCADE'), primary_key=True),
    db.Column('service_id', db.Integer, db.ForeignKey('services.id', ondelete='CASCADE'), primary_key=True),
    db.Column('custom_price', db.Integer, nullable=True),
    db.Column('custom_duration', db.Integer, nullable=True)
)

class Professional(db.Model):
    __tablename__ = 'professionals'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    
    # Multilingual Titles & Bios
    title_uz = db.Column(db.String(150), nullable=False)
    title_ru = db.Column(db.String(150), nullable=False)
    title_en = db.Column(db.String(150), nullable=False)
    
    bio_uz = db.Column(db.Text, nullable=False)
    bio_ru = db.Column(db.Text, nullable=False)
    bio_en = db.Column(db.Text, nullable=False)
    
    specialties_uz = db.Column(db.String(255), nullable=True)
    specialties_ru = db.Column(db.String(255), nullable=True)
    specialties_en = db.Column(db.String(255), nullable=True)
    
    skills_uz = db.Column(db.Text, nullable=True)
    skills_ru = db.Column(db.Text, nullable=True)
    skills_en = db.Column(db.Text, nullable=True)
    
    photo_url = db.Column(db.String(255), nullable=False)
    experience_years = db.Column(db.Integer, default=5)
    instagram_url = db.Column(db.String(200), nullable=True)
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    
    # Independent Notification Destinations
    telegram_chat_id = db.Column(db.String(100), nullable=True)
    sms_phone = db.Column(db.String(30), nullable=True)
    
    # Relationships
    services = db.relationship('Service', secondary=professional_services, backref=db.backref('professionals', lazy='dynamic'))
    schedules = db.relationship('WeeklySchedule', backref='professional', cascade='all, delete-orphan', lazy='dynamic')
    overrides = db.relationship('ScheduleOverride', backref='professional', cascade='all, delete-orphan', lazy='dynamic')
    portfolio_items = db.relationship('PortfolioItem', backref='professional', cascade='all, delete-orphan', lazy='dynamic', order_by='PortfolioItem.sort_order')
    appointments = db.relationship('Appointment', backref='professional', lazy='dynamic')
    reviews = db.relationship('Review', backref='professional', cascade='all, delete-orphan', lazy='dynamic')
    notification_logs = db.relationship('NotificationLog', backref='professional', lazy='dynamic')

class ServiceCategory(db.Model):
    __tablename__ = 'service_categories'
    
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    name_uz = db.Column(db.String(100), nullable=False)
    name_ru = db.Column(db.String(100), nullable=False)
    name_en = db.Column(db.String(100), nullable=False)
    sort_order = db.Column(db.Integer, default=0)
    
    services = db.relationship('Service', backref='category', lazy='dynamic')

class Service(db.Model):
    __tablename__ = 'services'
    
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('service_categories.id', ondelete='SET NULL'), nullable=True)
    slug = db.Column(db.String(80), unique=True, nullable=False)
    
    name_uz = db.Column(db.String(150), nullable=False)
    name_ru = db.Column(db.String(150), nullable=False)
    name_en = db.Column(db.String(150), nullable=False)
    
    description_uz = db.Column(db.Text, nullable=True)
    description_ru = db.Column(db.Text, nullable=True)
    description_en = db.Column(db.Text, nullable=True)
    
    target_audience = db.Column(db.String(20), default='unisex') # men, women, unisex
    base_price = db.Column(db.Integer, nullable=False) # In UZS (e.g. 180000)
    duration_minutes = db.Column(db.Integer, nullable=False) # e.g. 45
    image_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    
    appointments = db.relationship('Appointment', backref='service', lazy='dynamic')

class WeeklySchedule(db.Model):
    __tablename__ = 'weekly_schedules'
    
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='CASCADE'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False) # 0=Monday ... 6=Sunday
    is_working = db.Column(db.Boolean, default=True)
    start_time = db.Column(db.String(5), default='09:00') # HH:MM
    end_time = db.Column(db.String(5), default='20:00')   # HH:MM
    break_start = db.Column(db.String(5), default='13:00')
    break_end = db.Column(db.String(5), default='14:00')
    
    __table_args__ = (
        db.UniqueConstraint('professional_id', 'day_of_week', name='uq_pro_day'),
    )

class ScheduleOverride(db.Model):
    __tablename__ = 'schedule_overrides'
    
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='CASCADE'), nullable=False)
    override_date = db.Column(db.Date, nullable=False, index=True)
    is_available = db.Column(db.Boolean, default=False) # False = day off / holiday, True = custom working hours
    start_time = db.Column(db.String(5), nullable=True)
    end_time = db.Column(db.String(5), nullable=True)
    reason = db.Column(db.String(255), nullable=True)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    reference_code = db.Column(db.String(32), unique=True, nullable=False, index=True)
    
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='RESTRICT'), nullable=False, index=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.id', ondelete='RESTRICT'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    # Customer Details
    customer_name = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(30), nullable=False, index=True)
    customer_email = db.Column(db.String(120), nullable=True)
    customer_note = db.Column(db.Text, nullable=True) # Private note from customer to pro
    
    # Appointment Timing
    appointment_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.String(5), nullable=False) # "14:30"
    end_time = db.Column(db.String(5), nullable=False)   # "15:15"
    duration_minutes = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    
    # Status
    status = db.Column(db.String(20), default=BookingStatus.PENDING.value, nullable=False, index=True)
    rejection_reason = db.Column(db.String(255), nullable=True)
    cancellation_reason = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    notification_logs = db.relationship('NotificationLog', backref='appointment', lazy='dynamic')
    
    # Index for fast slot conflict queries
    __table_args__ = (
        db.Index('idx_pro_date_status', 'professional_id', 'appointment_date', 'status'),
    )

class PortfolioItem(db.Model):
    __tablename__ = 'portfolio_items'
    
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='CASCADE'), nullable=False, index=True)
    
    title_uz = db.Column(db.String(150), nullable=False)
    title_ru = db.Column(db.String(150), nullable=False)
    title_en = db.Column(db.String(150), nullable=False)
    
    category = db.Column(db.String(50), default='styling') # men_cut, beard, women_cut, color, treatment, styling
    image_url = db.Column(db.String(255), nullable=False)
    before_image_url = db.Column(db.String(255), nullable=True) # Optional before photo for before/after comparison
    video_url = db.Column(db.String(255), nullable=True)
    
    is_featured = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='CASCADE'), nullable=False, index=True)
    customer_name = db.Column(db.String(100), nullable=False)
    rating = db.Column(db.Integer, default=5, nullable=False) # 1 to 5
    comment = db.Column(db.Text, nullable=False)
    service_name = db.Column(db.String(100), nullable=True)
    is_verified = db.Column(db.Boolean, default=True)
    is_approved = db.Column(db.Boolean, default=True) # Public moderation
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class NotificationLog(db.Model):
    __tablename__ = 'notification_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointments.id', ondelete='SET NULL'), nullable=True)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='SET NULL'), nullable=True)
    
    channel = db.Column(db.String(20), nullable=False) # telegram, sms
    recipient = db.Column(db.String(100), nullable=False) # Chat ID or phone
    payload_text = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending') # delivered, failed, pending
    provider_response = db.Column(db.Text, nullable=True)
    error_details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class StudioSetting(db.Model):
    __tablename__ = 'studio_settings'
    
    key = db.Column(db.String(64), primary_key=True)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.String(255), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    professional_id = db.Column(db.Integer, db.ForeignKey('professionals.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        db.UniqueConstraint('user_id', 'professional_id', name='uq_user_pro_fav'),
    )
