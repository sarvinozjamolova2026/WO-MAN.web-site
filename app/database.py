from datetime import date, datetime, timedelta
from app.models import (
    db, User, Professional, ServiceCategory, Service,
    WeeklySchedule, ScheduleOverride, PortfolioItem, Review, StudioSetting,
    BookingStatus, Appointment
)

def seed_database():
    """Populate database with initial production-ready data for WO&MAN Barbershop."""
    
    # Check if already seeded with new data
    if User.query.filter_by(username='pro_akrom').first():
        return

    # Clear old data if exists to ensure clean state
    try:
        db.session.query(Appointment).delete()
        db.session.query(PortfolioItem).delete()
        db.session.query(Review).delete()
        db.session.query(WeeklySchedule).delete()
        db.session.query(ScheduleOverride).delete()
        db.session.query(Professional).delete()
        db.session.query(Service).delete()
        db.session.query(ServiceCategory).delete()
        db.session.query(User).delete()
        db.session.query(StudioSetting).delete()
        db.session.commit()
    except Exception:
        db.session.rollback()

    # 1. Admin Account
    admin = User(
        username='admin',
        email='admin@woandman.uz',
        phone='+998979775994',
        role='admin',
        full_name='WO&MAN Boshqaruvchi'
    )
    admin.set_password('Admin2026!WM')
    db.session.add(admin)

    # 2. Service Categories (Barbershop Focused)
    cat_hair = ServiceCategory(slug='hair', name_uz='Soch xizmatlari', name_ru='Стрижки и укладка', name_en="Hair Services", sort_order=1)
    cat_beard = ServiceCategory(slug='beard', name_uz='Soqol va yuz parvarishi', name_ru='Борода и уход за лицом', name_en="Beard & Face Care", sort_order=2)
    cat_vip = ServiceCategory(slug='vip', name_uz='VIP & SPA muolajalar', name_ru='VIP & SPA процедуры', name_en="VIP & SPA Rituals", sort_order=3)
    db.session.add_all([cat_hair, cat_beard, cat_vip])
    db.session.flush()

    # 3. Exact 10 Services from Official WO&MAN Price List
    services_data = [
        {
            'category_id': cat_hair.id,
            'slug': 'soch-olish',
            'name_uz': 'Soch olish',
            'name_ru': 'Стрижка волос',
            'name_en': "Men's Haircut",
            'description_uz': 'Klassik va zamonaviy uslubdagi individual erkaklar soch turmagi, bosh yuvish va stilizatsiya.',
            'description_ru': 'Мужская стрижка с учетом формы лица, мытье головы и профессиональный стайлинг.',
            'description_en': 'Signature precision haircut tailored to head shape, hair wash, and professional finish.',
            'target_audience': 'men',
            'base_price': 60000,
            'duration_minutes': 35,
            'image_url': '/static/images/portfolio/work-1-after.svg',
            'sort_order': 1
        },
        {
            'category_id': cat_hair.id,
            'slug': 'soch-soqol',
            'name_uz': 'Soch soqol',
            'name_ru': 'Стрижка + Борода',
            'name_en': 'Haircut & Beard Combo',
            'description_uz': 'To‘liq kompleks: soch turmagi, soqolni tekislash, aniq kontur chiziqlari va qulay parvarish.',
            'description_ru': 'Комплексный уход: стрижка волос, моделирование бороды и оформление контуров.',
            'description_en': 'Complete package: precision haircut, beard contouring, and hot towel finish.',
            'target_audience': 'men',
            'base_price': 100000,
            'duration_minutes': 60,
            'image_url': '/static/images/portfolio/work-2-after.svg',
            'sort_order': 2
        },
        {
            'category_id': cat_hair.id,
            'slug': 'detskiy',
            'name_uz': 'Detskiy (Bolalar soch turmagi)',
            'name_ru': 'Детская стрижка',
            'name_en': "Kids Haircut",
            'description_uz': 'Bolalar uchun qulay, sabrli va professional yondashuv asosida chiroyli soch turmagi.',
            'description_ru': 'Стрижка для мальчиков с максимальным вниманием, заботой и стильным результатом.',
            'description_en': 'Patient and stylish haircut tailored specially for boys and teenagers.',
            'target_audience': 'men',
            'base_price': 50000,
            'duration_minutes': 30,
            'image_url': '/static/images/portfolio/work-3-after.svg',
            'sort_order': 3
        },
        {
            'category_id': cat_hair.id,
            'slug': 'ukladka',
            'name_uz': 'Ukladka (Stilizatsiya)',
            'name_ru': 'Укладка волос',
            'name_en': 'Hair Styling & Blowdry',
            'description_uz': 'Fen, brossh va maxsus fiksatsiya vositalari bilan kun bo‘yi turadigan soch turmagi.',
            'description_ru': 'Профессиональная укладка волос феном и премиальными стайлинг-средствами.',
            'description_en': 'Voluminous blowdry and long-lasting styling with premium grooming pomade.',
            'target_audience': 'men',
            'base_price': 50000,
            'duration_minutes': 20,
            'image_url': '/static/images/portfolio/work-5-after.svg',
            'sort_order': 4
        },
        {
            'category_id': cat_hair.id,
            'slug': 'soch-boyash',
            'name_uz': 'Soch boyash (Kamuflyaj)',
            'name_ru': 'Окрашивание волос / Камуфляж седины',
            'name_en': 'Hair Coloring & Grey Blending',
            'description_uz': 'Oq sochlarni tabiiy yopish, bir xil jilo berish va yoshartiruvchi kamuflyaj muolajasi.',
            'description_ru': 'Естественное тонирование седины и придание волосам глубокого натурального оттенка.',
            'description_en': 'Discreet grey camouflage and natural hair tinting for a refreshed look.',
            'target_audience': 'men',
            'base_price': 50000,
            'duration_minutes': 40,
            'image_url': '/static/images/portfolio/color-1.svg',
            'sort_order': 5
        },
        {
            'category_id': cat_beard.id,
            'slug': 'soqol',
            'name_uz': 'Soqol (Dizayn va shakl)',
            'name_ru': 'Моделирование бороды',
            'name_en': 'Beard Trimming & Shaping',
            'description_uz': 'Soqol geometriyasini tekislash, xavfsiz ustara bilan tozalash va moylash.',
            'description_ru': 'Четкие контуры, придание формы бороде и нанесение смягчающего масла.',
            'description_en': 'Straight-razor edge lineup, length graduation, and beard oil nourishment.',
            'target_audience': 'men',
            'base_price': 40000,
            'duration_minutes': 25,
            'image_url': '/static/images/portfolio/beard-1.svg',
            'sort_order': 6
        },
        {
            'category_id': cat_beard.id,
            'slug': 'vosk',
            'name_uz': 'Vosk (Depilyatsiya)',
            'name_ru': 'Удаление волос воском',
            'name_en': 'Wax Depilation',
            'description_uz': 'Burun, quloq va yonoq sohasidagi ortiqcha tuklarni og‘riqsiz vosk bilan tozalash.',
            'description_ru': 'Аккуратное удаление нежелательных волос в зоне носа, ушей и щек горячим воском.',
            'description_en': 'Clean and swift wax removal of unwanted hair from ears, nose, and cheek lines.',
            'target_audience': 'men',
            'base_price': 30000,
            'duration_minutes': 15,
            'image_url': '/static/images/portfolio/work-1-detail.svg',
            'sort_order': 7
        },
        {
            'category_id': cat_beard.id,
            'slug': 'maska',
            'name_uz': 'Maska (Yuz terisini tozalash)',
            'name_ru': 'Очищающая маска для лица',
            'name_en': 'Purifying Black Mask Facial',
            'description_uz': 'Teshikchalarni chuqur tozalovchi qora maska, ortiqcha yog‘ni bartaraf etish va namlantirish.',
            'description_ru': 'Глубокое очищение пор черной маской, сужение пор и тонизирование кожи.',
            'description_en': 'Deep pore-cleansing peel-off mask, sebum balance, and cooling skin hydration.',
            'target_audience': 'men',
            'base_price': 40000,
            'duration_minutes': 20,
            'image_url': '/static/images/portfolio/spa-2.svg',
            'sort_order': 8
        },
        {
            'category_id': cat_vip.id,
            'slug': 'massaj-golovi',
            'name_uz': 'Massaj golovi (Bosh massaji)',
            'name_ru': 'Релакс-массаж головы',
            'name_en': 'Scalp Massage & Relaxation',
            'description_uz': 'Qon aylanishini kuchaytiruvchi, bosh og‘rig‘i va charchoqni ketkazuvchi yoqimli bosh massaji.',
            'description_ru': 'Снятие усталости, улучшение микроциркуляции и тотальное расслабление.',
            'description_en': 'Acupressure tension-relief head and scalp massage for optimal relaxation.',
            'target_audience': 'men',
            'base_price': 50000,
            'duration_minutes': 20,
            'image_url': '/static/images/portfolio/spa-1.svg',
            'sort_order': 9
        },
        {
            'category_id': cat_vip.id,
            'slug': 'kuyov-obroz',
            'name_uz': 'Kuyov obroz (VIP Grooming)',
            'name_ru': 'Образ жениха (VIP Куёв образ)',
            'name_en': 'Groom VIP Wedding Package',
            'description_uz': 'To‘y va tantanalar uchun to‘liq VIP parvarish: soch, soqol, yuz maskasi, bosh massaji, vosk va to‘liq stilizatsiya.',
            'description_ru': 'Полная подготовка жениха к свадьбе: стрижка, моделирование бороды, спа-уход за лицом, массаж и безупречный стайлинг.',
            'description_en': 'Comprehensive wedding transformation: signature haircut, beard grooming, facial cleansing, scalp massage, and premium finish.',
            'target_audience': 'men',
            'base_price': 400000,
            'duration_minutes': 120,
            'image_url': '/static/images/portfolio/men-cut-2.svg',
            'sort_order': 10
        }
    ]

    services_objs = []
    for s_data in services_data:
        srv = Service(**s_data)
        db.session.add(srv)
        services_objs.append(srv)
    db.session.flush()

    # 4. The Three Barbers from User's Uploaded Photos
    pros_data = [
        {
            'username': 'pro_akrom',
            'email': 'akrom@woandman.uz',
            'phone': '+998975487797',
            'name': 'Akrom',
            'slug': 'akrom',
            'title_uz': 'Master Barber & Erkaklar stilisti',
            'title_ru': 'Мастер-барбер & Стилист',
            'title_en': 'Master Barber & Stylist',
            'bio_uz': "Akrom — zamonaviy va klassik erkaklar soch turmaklari bo‘yicha tajribali mutaxassis. Har bir mijozning yuz tuzilishi va soch o‘sish yo‘nalishiga mos individual fade, qirqish va kundalik parvarish uslubini yaratadi.",
            'bio_ru': "Акром — опытный мастер классических и современных стрижек. Индивидуальный подход к каждому гостю, безупречные фейды и стильные детские стрижки.",
            'bio_en': "Akrom specializes in modern skin fades, classic scissor cuts, and personalized styling tailored to individual cranial profiles.",
            'specialties_uz': "Klassik soch turmagi, Skin Fade, Detskiy, Soch soqol kompleksi",
            'specialties_ru': "Классические стрижки, фейд, детские стрижки, уход за бородой",
            'specialties_en': "Classic Scissor Cuts, Skin Fade, Kids Grooming, Beard Trimming",
            'skills_uz': "Fade texnikalari • Qaychi bilan ishlash • Bolalar turmagi • Ukladka",
            'skills_ru': "Техники фейда • Ножницы • Детские стрижки • Премиум укладка",
            'skills_en': "Precision Fades • Shear Sculpting • Kid Haircuts • Styling",
            'experience_years': 4,
            'photo_url': '/static/images/pros/akrom.jpg',
            'instagram_url': 'https://instagram.com/wo_man_yangiyol',
            'telegram_chat_id': '',
            'sms_phone': '+998975487797',
            'sort_order': 1
        },
        {
            'username': 'pro_axror',
            'email': 'axror@woandman.uz',
            'phone': '+998770717837',
            'name': 'Axror',
            'slug': 'axror',
            'title_uz': 'Senior Barber & Soqol dizayneri',
            'title_ru': 'Ведущий барбер & Дизайнер бороды',
            'title_en': 'Senior Barber & Beard Architect',
            'bio_uz': "Axror — soqol shakllantirish, geometrik konturlar, vosk va soch-soqol kompleks parvarishi bo‘yicha usta. Benuqson aniqlik, xavfsiz ustara bilan ishlash va qulaylik tarafdori.",
            'bio_ru': "Ахрор — мастер идеальных контуров бороды, точного бритья и комплексного ухода. Филигранная работа опасной бритвой и восковая депиляция.",
            'bio_en': "Axror is renowned for razor-sharp beard architecture, clean straight-razor detailing, and full-service grooming packages.",
            'specialties_uz': "Soqol dizayni, Soch soqol, Vosk, Issiq sochiq parvarishi",
            'specialties_ru': "Моделирование бороды, комплексная стрижка, депиляция воском, спа-бритье",
            'specialties_en': "Beard Sculpting, Complete Combo, Waxing, Steamed Hot Towel",
            'skills_uz': "Ustara bilan ishlash • Soqol konturi • Vosk depilyatsiyasi • Fen stilizatsiyasi",
            'skills_ru': "Опасная бритва • Геометрия бороды • Воск • Укладка",
            'skills_en': "Straight Razor • Beard Geometry • Hot Waxing • Styling",
            'experience_years': 5,
            'photo_url': '/static/images/pros/axror.jpg',
            'instagram_url': 'https://instagram.com/wo_man_yangiyol',
            'telegram_chat_id': '',
            'sms_phone': '+998770717837',
            'sort_order': 2
        },
        {
            'username': 'pro_jamoliddin',
            'email': 'jamoliddin@woandman.uz',
            'phone': '+998979775994',
            'name': 'Jamoliddin',
            'slug': 'jamoliddin',
            'title_uz': 'Head Barber & Studiya yetakchisi',
            'title_ru': 'Главный барбер & Основатель студии',
            'title_en': 'Head Barber & Studio Lead',
            'bio_uz': "Jamoliddin — WO&MAN Barbershop yetakchi ustasi. Kuyov obrazlari (VIP Grooming), bosh massaji, soch bo‘yash va premium parvarish bo‘yicha oliy toifali usta.",
            'bio_ru': "Жамолиддин — ведущий мастер и основатель барбершопа. Эксперт по созданию свадебных образов жениха, тонированию седины и релакс-массажу головы.",
            'bio_en': "Jamoliddin is the head master and studio founder, renowned for VIP groom transformations, relaxing head massages, and restorative treatments.",
            'specialties_uz': "Kuyov obrozi VIP, Massaj golovi, Soch boyash, Soch soqol",
            'specialties_ru': "Образ жениха VIP, массаж головы, камуфляж седины, стрижка и борода",
            'specialties_en': "Groom Wedding Package, Scalp Massage, Hair Coloring, Combo Care",
            'skills_uz': "Kuyov stilistikasi • Bosh massaji • Rang berish & Kamuflyaj • SPA muolajalar",
            'skills_ru': "Свадебный стайлинг • Массаж • Камуфляж седины • SPA уход",
            'skills_en': "Wedding VIP Styling • Head Acupressure • Grey Camouflage • SPA Rituals",
            'experience_years': 7,
            'photo_url': '/static/images/pros/jamoliddin.jpg',
            'instagram_url': 'https://instagram.com/wo_man_yangiyol',
            'telegram_chat_id': '',
            'sms_phone': '+998979775994',
            'sort_order': 3
        }
    ]

    for p_idx, p_data in enumerate(pros_data):
        user = User(
            username=p_data['username'],
            email=p_data['email'],
            phone=p_data['phone'],
            role='professional',
            full_name=p_data['name']
        )
        user.set_password(p_data.get('password', 'Pro2026!WM'))
        db.session.add(user)
        db.session.flush()

        pro = Professional(
            user_id=user.id,
            slug=p_data['slug'],
            name=p_data['name'],
            title_uz=p_data['title_uz'],
            title_ru=p_data['title_ru'],
            title_en=p_data['title_en'],
            bio_uz=p_data['bio_uz'],
            bio_ru=p_data['bio_ru'],
            bio_en=p_data['bio_en'],
            specialties_uz=p_data['specialties_uz'],
            specialties_ru=p_data['specialties_ru'],
            specialties_en=p_data['specialties_en'],
            skills_uz=p_data['skills_uz'],
            skills_ru=p_data['skills_ru'],
            skills_en=p_data['skills_en'],
            experience_years=p_data['experience_years'],
            photo_url=p_data['photo_url'],
            instagram_url=p_data['instagram_url'],
            telegram_chat_id=p_data['telegram_chat_id'],
            sms_phone=p_data['sms_phone'],
            sort_order=p_data['sort_order'],
            is_active=True
        )
        db.session.add(pro)
        db.session.flush()

        # All 3 barbers offer all the official price list services!
        for srv in services_objs:
            pro.services.append(srv)

        # Weekly Schedule (Working every day 09:00 - 21:00 with lunch break 13:00 - 14:00)
        # Shift balancing: Akrom off on Monday, Axror off on Tuesday, Jamoliddin off on Wednesday
        for day in range(7):
            is_work = True
            if p_idx == 0 and day == 0: # Akrom Monday off
                is_work = False
            elif p_idx == 1 and day == 1: # Axror Tuesday off
                is_work = False
            elif p_idx == 2 and day == 2: # Jamoliddin Wednesday off
                is_work = False

            sched = WeeklySchedule(
                professional_id=pro.id,
                day_of_week=day,
                is_working=is_work,
                start_time='09:00',
                end_time='21:00',
                break_start='13:00',
                break_end='14:00'
            )
            db.session.add(sched)

        # Authentic portfolio items for each barber
        portfolio_seeds = [
            {
                'title_uz': f"{pro.name} — Mualliflik soch va soqol ishi",
                'title_ru': f"{pro.name} — Авторская работа (Стрижка и борода)",
                'title_en': f"{pro.name} — Signature Cut & Beard",
                'category': 'men_cut',
                'image_url': f'/static/images/portfolio/work-{p_idx+1}-after.svg',
                'before_image_url': f'/static/images/portfolio/work-{p_idx+1}-before.svg',
                'is_featured': True,
                'sort_order': 1
            },
            {
                'title_uz': f"{pro.name} — Soqol geometriyasi va toza kontur",
                'title_ru': f"{pro.name} — Четкие контуры бороды",
                'title_en': f"{pro.name} — Beard Geometry & Lineup",
                'category': 'beard',
                'image_url': f'/static/images/portfolio/work-{p_idx+1}-detail.svg',
                'before_image_url': None,
                'is_featured': True,
                'sort_order': 2
            }
        ]
        for pf in portfolio_seeds:
            item = PortfolioItem(
                professional_id=pro.id,
                title_uz=pf['title_uz'],
                title_ru=pf['title_ru'],
                title_en=pf['title_en'],
                category=pf['category'],
                image_url=pf['image_url'],
                before_image_url=pf['before_image_url'],
                is_featured=pf['is_featured'],
                is_approved=True,
                sort_order=pf['sort_order']
            )
            db.session.add(item)

        # Verified reviews
        rev = Review(
            professional_id=pro.id,
            customer_name="Sardor Alimov",
            rating=5,
            comment=f"{pro.name} haqiqiy usta! Soch va soqolni ideal qilib oldilar. Studiyadagi muhit juda zo‘r, tavsiya qilaman.",
            service_name="Soch soqol",
            is_verified=True,
            is_approved=True
        )
        db.session.add(rev)

    # 5. Studio Settings (Matching the uploaded price list & details)
    initial_settings = [
        ('brand_name', 'WO&MAN', 'Brend rasmiy nomi'),
        ('brand_logo_path', '/static/brand/official_logo.jpg', 'Asosiy logotip fayl manzili'),
        ('brand_price_list_path', '/static/brand/price_list.jpg', 'Rasmiy narxlar ro‘yxati (Price list)'),
        ('brand_favicon_path', '/static/brand/favicon.svg', 'Favicon manzili'),
        ('studio_phone', '+998 97 977 5994', 'Aloqa telefon raqami'),
        ('studio_instagram', 'https://instagram.com/wo_man_yangiyol', 'Rasmiy Instagram sahifa'),
        ('studio_address', "Yangiyo'l shahri, WO&MAN Barbershop", 'Studiyaning jismoniy manzili'),
        ('studio_working_hours', '09:00 - 21:00 (Har kuni / Dam olish kunlarisiz)', 'Studiyaning ish vaqti'),
        ('studio_tagline', 'Стиль • Качество • Уверенность', 'Brend shiori'),
        ('telegram_bot_token', '', 'Telegram Bot rasmiy API tokeni'),
        ('telegram_admin_chat_id', '', 'Boshqaruvchi Telegram Chat ID'),
        ('sms_provider', 'mock', 'SMS shlyuzi (mock, eskiz, playmobile, twilio)'),
        ('min_booking_notice_hours', '1', 'Yozilishdan oldingi minimal muddat (soat)'),
        ('max_booking_advance_days', '30', 'Oldindan band qilish maksimal muddati (kun)'),
        ('appointment_buffer_minutes', '5', 'Qabullar orasidagi texnik tanaffus (daqiqa)'),
        ('manual_approval_required', 'false', 'Yangi yozilishlarni qo‘lda tasdiqlash zarurati')
    ]
    for k, v, desc in initial_settings:
        db.session.add(StudioSetting(key=k, value=v, description=desc))

    # Commit all seed data
    db.session.commit()
