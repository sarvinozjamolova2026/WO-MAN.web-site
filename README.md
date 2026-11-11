# WO&MAN — Premium Unisex Grooming & Beauty Platform

> **Bespoke unisex salon and grooming lounge in Tashkent.**  
> Built with Flask, SQLAlchemy 2.0, high-end editorial aesthetics (Obsidian Black, Deep Graphite, Warm Ivory, Champagne Gold), multi-language internationalization (Uzbek Latin default, Russian, English), real-time database-backed availability engine with concurrency protection, independent Telegram Bot routing for the 5 professionals, and dedicated administrative & professional portals.

---

## 1. Loyiha haqida va Asosiy Imkoniyatlar (Platform Highlights)

1. **Brend va Vizual Identika (Brand Identity & Logo):**
   - Rasmiy nom: **WO&MAN**
   - Logotip aktivlari joylashuvi: `app/static/brand/logo.svg` va `app/static/brand/favicon.svg`.
   - Administrator panelida yangi rasmiy logotip faylini (PNG, SVG, WEBP) 1 tugma bilan yuklash va butun sayt bo‘ylab avtomatik yangilash imkoniyati (`/admin/settings`).
   - Hashamatli ranglar palitrasi: Obsidian qora (`#111111`), Grafit (`#202020`), Iliq fil suyagi (`#F5F0E8`), Shampan oltin (`#C5A46D`).

2. **Besh Mustaqil Mutaxassis (The Five Initial Professionals):**
   - **Aziz Karimov** (`aziz-karimov`) — *Head Barber & Erkaklar uslubi rahbari*
   - **Kamila Rahimova** (`kamila-rahimova`) — *Bosh stilist & Murakkab bo‘yash bo‘yicha Art Director*
   - **Jamshid Aliev** (`jamshid-aliev`) — *Master Barber & Erkaklar parvarishi mutaxassisi*
   - **Madina Yusupova** (`madina-yusupova`) — *Senior Hair Stylist & Soch sog‘lomlashtirish ustasi*
   - **Shavkat Rustamov** (`shavkat-rustamov`) — *Stilist & Estetik parvarish bo‘yicha mutaxassis*
   - Har bir mutaxassis o‘zining mustaqil sahifasiga (`/professionals/<slug>`), haftalik jadvaliga, mualliflik portfoliosiga va shaxsiy Telegram Chat ID bildirishnoma yo‘nalishiga ega.

3. **Jonli Taqvim va Band Qilish Tizimi (Availability Engine & Concurrency):**
   - Har bir ustaning individual ish soatlari, dam olish kunlari va tushlik tanaffuslari (13:00–14:00) hisobga olinadi.
   - Tranzaksiyaviy server-side tekshiruv: bir vaqtning o‘zida ikki mijoz aynan bir vaqtni band qilganda, poyga holati (race condition) oldi olinadi va ikkinchi so‘rov darhol `409 Conflict` xatosi bilan rad etiladi.
   - Har bir muvaffaqiyatli buyurtma uchun unikal kod generatsiya qilinadi: masalan, `WM-2026-X8B2K`.
   - Apple Calendar, Google Calendar va Outlook uchun `.ics` formatida taqvimga qo‘shish fayli avtomatik yaratiladi.

4. **Mustaqil Telegram va SMS Xabarnomalari (Notification Routing):**
   - Bitta rasmiy Telegram Bot orqali barcha 5 nafar mutaxassisning shaxsiy Telegram Chat ID lariga alohida xabarlar yo‘naltiriladi.
   - Aziz Karimovga tushgan buyurtma faqat Azizning shaxsiy Telegramiga boradi.
   - Administrator panelida har bir mutaxassis uchun "Sinov xabari yuborish" tugmasi mavjud.
   - SMS provayder adapteri (`Mock`, `Eskiz.uz`, `PlayMobile`, `Twilio`) integratsiya qilingan.
   - Barcha yetkazilgan va xatolik bergan xabarlar `notification_logs` audit jadvalida qayd etiladi.

5. **Ko‘p tilli muhit (i18n):**
   - Asosiy til: **O‘zbek tili (Lotin alifbosi)**
   - To‘liq qo‘llab-quvvatlanuvchi tillar: **Rus tili (RU)** va **Ingliz tili (EN)**
   - Sayt navigatsiyasidagi til tugmalari orqali lahzada almashish.

6. **Interaktiv Portfolio va Oldin/Keyin (Before & After Slider):**
   - Har bir usta o‘z ishlarini "Oldin" va "Keyin" rasmlari bilan yuklashi mumkin.
   - Foydalanuvchilar maxsus slayd tutqichini surib o‘zgarishlarni bevosita solishtirishlari mumkin.

7. **Xavfsizlik va Ma'lumotlar Izolyatsiyasi:**
   - Shaxsiy kabinetga kirishda parollar `Werkzeug scrypt` algoritmi bilan xeshlanadi.
   - Mutaxassis faqat o‘zining buyurtmalari va mijoz izohlarini ko‘ra oladi (boshqa ustalarning ma'lumotlariga kirish bloklangan).

---

## 2. Foydalanuvchi hisoblari va Demo kirish ma'lumotlari

Tizimda rollar bo‘yicha quyidagi sinov hisoblari mavjud:

| Rol | Foydalanuvchi nomi | Maxfiy parol | Kirish havolasi |
|---|---|---|---|
| **Bosh Administrator** | `admin` | `Admin2026!WM` | `/admin/dashboard` |
| **Aziz Karimov** (Head Barber) | `pro_aziz` | `Pro2026!WM` | `/pro/dashboard` |
| **Kamila Rahimova** (Art Director) | `pro_kamila` | `Pro2026!WM` | `/pro/dashboard` |
| **Jamshid Aliev** (Master Barber) | `pro_jamshid` | `Pro2026!WM` | `/pro/dashboard` |
| **Madina Yusupova** (Senior Stylist) | `pro_madina` | `Pro2026!WM` | `/pro/dashboard` |
| **Shavkat Rustamov** (Stylist) | `pro_shavkat` | `Pro2026!WM` | `/pro/dashboard` |

---

## 3. Loyihani mahalliy muhitda ishga tushirish (Local Setup)

### 1-qadam: Virtual muhitni faollashtirish
PowerShell terminalida:
```powershell
cd C:\Users\User\.gemini\antigravity\scratch\wo-and-man
.\venv\Scripts\Activate.ps1
```

### 2-qadam: Kutubxonalarni o‘rnatish (agar yangi muhit bo‘lsa)
```powershell
pip install -r requirements.txt
```

### 3-qadam: Ilovani ishga tushirish
```powershell
python run.py
```
Ilova `http://127.0.0.1:5000` manzilida ishga tushadi.

---

## 4. Telegram Botni ulash bo‘yicha qo‘llanma

1. Telegramda `@BotFather` orqali yangi bot yarating (`/newbot`) va API tokenni oling.
2. Saytning **Administrator Paneli**ga kiring: `http://127.0.0.1:5000/login` (`admin` / `Admin2026!WM`).
3. **"Bildirishnomalar & Telegram"** bo‘limiga o‘ting.
4. Olingan tokenni kiriting va **"Botni saqlash"** tugmasini bosing.
5. Har bir mutaxassisning Telegram Chat ID raqamini kiriting:
   - Chat ID ni bilish uchun har bir usta `@userinfobot` ga `/start` yuborishi kifoya.
6. Har bir ustaning kartasidagi **"Sinov xabari yuborish"** tugmasini bosib integratsiyani tekshiring.

---

## 5. Avtomatlashtirilgan testlarni ishga tushirish

Barcha 12 ta qat'iy test stsenariylari (mavjudlik algoritmi, poyga holati/konfliktlar, 409 xatosi, bildirishnomalarni alohida yo‘naltirish, xavfsizlik va tillar) quyidagi buyruq orqali sinovdan o‘tkaziladi:

```powershell
$env:PYTHONPATH="C:\Users\User\.gemini\antigravity\scratch\wo-and-man"
.\venv\Scripts\python.exe -m pytest -c pytest.ini tests -v
```

Natija:
```
tests/test_professionals_and_services.py ... PASSED
tests/test_availability_and_concurrency.py ... PASSED
tests/test_notification_routing.py ... PASSED
tests/test_security_and_authorization.py ... PASSED
12 passed in 9.56s
```

---

## 6. Ishlab chiqarish (Production Deployment)

Loyiha standart WSGI arxitekturasi asosida yaratilgan va quyidagi usullarda oson joylashtiriladi:

### Gunicorn + Nginx + PostgreSQL (Linux VPS):
```bash
# PostgreSQL uchun .env faylida:
DATABASE_URL=postgresql://wo_user:wo_pass@localhost:5432/wo_and_man

# Gunicorn orqali ishga tushirish:
gunicorn -w 4 -b 127.0.0.1:5000 run:app
```

---

## 7. Loyiha tuzilmasi (Project Structure)

```
wo-and-man/
├── app/
│   ├── config.py             # Konfiguratsiya, vaqt mintaqasi, qoidalar
│   ├── models.py             # SQLAlchemy modellar (Besh mutaxassis, xizmatlar, buyurtmalar, loglar)
│   ├── database.py           # Dastlabki 5 usta va xizmatlarni avtomatik to‘ldirish
│   ├── i18n/
│   │   └── translations.py   # O‘zbekcha, Ruscha, Inglizcha lug‘atlar
│   ├── services/
│   │   ├── availability.py   # Bo‘sh vaqt oraliqlarini hisoblash va ziddiyatlarni bloklash
│   │   ├── booking.py        # Tranzaksiyaviy buyurtma va holatlar
│   │   └── notifications.py  # Shaxsiy Telegram va SMS yo‘naltirish
│   ├── routes/
│   │   ├── main.py           # Bosh sahifa, xizmatlar, portfolio, aloqa
│   │   ├── booking.py        # 5 bosqichli qabul vizardi va .ics yaratish
│   │   ├── auth.py           # Kirish va chiqish
│   │   ├── pro.py            # Mutaxassis shaxsiy kabineti
│   │   └── admin.py          # Boshqaruvchi ma'muri kabineti
│   ├── static/
│   │   ├── brand/            # Logotip va Favicon
│   │   ├── images/           # 5 ustaning badiiy portretlari va portfoliolar
│   │   ├── css/luxury.css    # Hashamatli dizayn tizimi
│   │   └── js/               # Vizard va Oldin/Keyin slayderi
│   └── templates/            # Jinja2 shablonlari
├── tests/                    # Pytest avtomatlashtirilgan testlar to‘plami
├── .env.example              # Namuna konfiguratsiya fayli
├── requirements.txt          # Kerakli paketlar
├── run.py                    # Kirish nuqtasi
└── README.md                 # To‘liq hujjat
```
