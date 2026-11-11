from flask import Blueprint, render_template, request, session, redirect, url_for, g
from app.models import db, Professional, Service, ServiceCategory, PortfolioItem, Review, StudioSetting
from app.i18n.translations import get_text

main_bp = Blueprint('main', __name__)

@main_bp.before_app_request
def load_locale_and_settings():
    # Detect language preference: session > query parameter > default 'uz'
    lang_param = request.args.get('lang')
    if lang_param in ['uz', 'ru', 'en']:
        session['lang'] = lang_param
    g.lang = session.get('lang', 'uz')
    g.t = lambda key, default=None: get_text(key, g.lang, default)
    
    # Brand logo path
    logo_setting = StudioSetting.query.filter_by(key='brand_logo_path').first()
    g.brand_logo_path = logo_setting.value if logo_setting and logo_setting.value else '/static/brand/official_logo.jpg'
    
    # Studio contact & brand settings
    phone_s = StudioSetting.query.filter_by(key='studio_phone').first()
    g.studio_phone = phone_s.value if phone_s else '+998 97 977 5994'
    
    insta_s = StudioSetting.query.filter_by(key='studio_instagram').first()
    g.studio_instagram = insta_s.value if insta_s else 'https://instagram.com/wo_man_yangiyol'
    
    addr_s = StudioSetting.query.filter_by(key='studio_address').first()
    g.studio_address = addr_s.value if addr_s else "Yangiyo'l shahri, WO&MAN Barbershop"
    
    hours_s = StudioSetting.query.filter_by(key='studio_working_hours').first()
    g.studio_working_hours = hours_s.value if hours_s else '09:00 - 21:00 (Har kuni)'
    
    price_s = StudioSetting.query.filter_by(key='brand_price_list_path').first()
    g.brand_price_list_path = price_s.value if price_s else '/static/brand/price_list.jpg'

@main_bp.route('/')
def home():
    # Five initial professionals
    professionals = Professional.query.filter_by(is_active=True).order_by(Professional.sort_order.asc()).all()
    # Featured services
    categories = ServiceCategory.query.order_by(ServiceCategory.sort_order.asc()).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.sort_order.asc()).all()
    # Featured portfolio items with before/after comparisons
    portfolio_items = PortfolioItem.query.filter_by(is_approved=True, is_featured=True).order_by(PortfolioItem.sort_order.asc()).all()
    # Verified customer reviews
    reviews = Review.query.filter_by(is_approved=True).limit(6).all()
    
    return render_template(
        'home.html',
        professionals=professionals,
        categories=categories,
        services=services,
        portfolio_items=portfolio_items,
        reviews=reviews
    )

@main_bp.route('/services')
def services():
    categories = ServiceCategory.query.order_by(ServiceCategory.sort_order.asc()).all()
    services = Service.query.filter_by(is_active=True).order_by(Service.sort_order.asc()).all()
    return render_template('services.html', categories=categories, services=services)

@main_bp.route('/professionals')
def professionals():
    pros = Professional.query.filter_by(is_active=True).order_by(Professional.sort_order.asc()).all()
    return render_template('professionals.html', professionals=pros)

@main_bp.route('/professionals/<slug>')
def professional_detail(slug):
    pro = Professional.query.filter_by(slug=slug, is_active=True).first_or_404()
    portfolio = pro.portfolio_items.filter_by(is_approved=True).all()
    reviews = pro.reviews.filter_by(is_approved=True).all()
    weekly_schedules = pro.schedules.order_by(db.text('day_of_week ASC')).all()
    
    return render_template(
        'professional_detail.html',
        pro=pro,
        portfolio=portfolio,
        reviews=reviews,
        weekly_schedules=weekly_schedules
    )

@main_bp.route('/portfolio')
def portfolio():
    category = request.args.get('category', 'all')
    query = PortfolioItem.query.filter_by(is_approved=True)
    if category != 'all':
        query = query.filter_by(category=category)
    items = query.order_by(PortfolioItem.sort_order.asc()).all()
    return render_template('portfolio.html', items=items, active_category=category)

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/privacy')
def privacy():
    return render_template('privacy.html')

@main_bp.route('/terms')
def terms():
    return render_template('terms.html')

@main_bp.route('/set-language/<lang>')
def set_language(lang):
    if lang in ['uz', 'ru', 'en']:
        session['lang'] = lang
    next_page = request.referrer or url_for('main.home')
    return redirect(next_page)
