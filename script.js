/* ==========================================================================
   WO&MAN BARBERSHOP — ENGINE & CLIENT CONTROLLER
   Glassmorphism UI • Telegram Bot Integration • Barber Cabinets • Admin Panel
   ========================================================================== */

// Default 10 Services from Official WO&MAN Price List
const DEFAULT_SERVICES = [
  { id: 'soch-olish', num: '01', name: 'Soch olish', category: 'hair', price: 60000, duration: 35, desc: "Klassik va zamonaviy uslub, individual soch turmagi, bosh yuvish va fenda stillashtirish." },
  { id: 'soch-soqol', num: '02', name: 'Soch soqol (Kompleks)', category: 'hair', price: 100000, duration: 60, desc: "To'liq kompleks: soch turmagi + soqol shakllantirish, toza geometrik kontur va issiq sochiq." },
  { id: 'detskiy', num: '03', name: 'Detskiy (Bolalar soch turmagi)', category: 'kids', price: 50000, duration: 30, desc: "Bolalar uchun sabrli, ehtiyotkor, xavfsiz va zamonaviy uslubdagi soch turmagi." },
  { id: 'ukladka', num: '04', name: 'Ukladka (Stilizatsiya)', category: 'hair', price: 50000, duration: 20, desc: "Premium pasta, loy va maxsus fiksatsiya vositalari yordamida sochni professional shakllantirish." },
  { id: 'soch-boyash', num: '05', name: 'Soch boyash (Kamuflyaj)', category: 'hair', price: 50000, duration: 40, desc: "Oq sochlarni tabiiy yashirish, rang berish va erkaklar uchun maxsus tonirovka muolajasi." },
  { id: 'soqol', num: '06', name: 'Soqol (Dizayn va shakl)', category: 'beard', price: 40000, duration: 25, desc: "Soqolni tekislash, aniq geometrik chiziqlar, ustara bilan tozalash va parvarishlash moyi." },
  { id: 'vosk', num: '07', name: 'Vosk (Depilyatsiya)', category: 'spa', price: 30000, duration: 15, desc: "Burun, quloq va yanoq sohasidagi ortiqcha tuklarni tez va og'riqsiz tozalash." },
  { id: 'maska', num: '08', name: 'Maska (Yuz tozalash)', category: 'spa', price: 40000, duration: 20, desc: "Qora nuqtalarni tozalovchi, yog'lanishni kamaytiruvchi va yuz terisini yoshartiruvchi maxsus niqob." },
  { id: 'massaj-golovi', num: '09', name: 'Massaj golovi (Bosh massaji)', category: 'spa', price: 50000, duration: 20, desc: "Qon aylanishini kuchaytiruvchi, charchoq va stressni yozuvchi relaksatsion bosh massaji." },
  { id: 'kuyov-obroz', num: '10', name: 'Kuyov obroz (VIP Kompleks)', category: 'vip', price: 400000, duration: 120, desc: "To'liq to'y paketi: soch, soqol, yuz terisini chuqur tozalash, bosh massaji, ukladka va fiksatsiya." }
];

// Resident Barbers Data
const BARBERS = {
  akrom: {
    id: 'akrom',
    name: 'Akrom',
    rank: 'Top Barber',
    phone: '+998975487797',
    phone_display: '+998 97 548 77 97',
    photo: 'app/static/images/pros/akrom.jpg',
    exp: '8 yil tajriba',
    skills: 'Klassik va zamonaviy soch turmaklari, Low/Mid Fade, soqol geometriyasi, toza chiziqlar.',
    days: 'Har kuni (Dushanba dam olish) • 09:00 - 21:00'
  },
  axror: {
    id: 'axror',
    name: 'Axror',
    rank: 'Master Barber',
    phone: '+998770717837',
    phone_display: '+998 77 071 78 37',
    photo: 'app/static/images/pros/axror.jpg',
    exp: '6 yil tajriba',
    skills: 'Zamonaviy erkaklar ukladkasi, bolalar soch turmagi (Detskiy), soqol qirqish, vosk va yuz parvarishi.',
    days: 'Har kuni (Seshanba dam olish) • 09:00 - 21:00'
  },
  jamoliddin: {
    id: 'jamoliddin',
    name: 'Jamoliddin',
    rank: 'VIP Master & Barber',
    phone: '+998979775994',
    phone_display: '+998 97 977 59 94',
    photo: 'app/static/images/pros/jamoliddin.jpg',
    exp: '7 yil tajriba',
    skills: 'Kuyov obrozi (Wedding VIP), bo\'yin va bosh massaji, soch boyash/kamuflyaj, SPA yuz parvarishi.',
    days: 'Har kuni (Chorshanba dam olish) • 09:00 - 21:00'
  }
};

// Available time slots (09:00 - 21:00)
const TIME_SLOTS = [
  "09:00", "09:40", "10:20", "11:00", "11:40",
  "12:20", "14:00", "14:40", "15:20", "16:00",
  "16:40", "17:20", "18:00", "18:40", "19:20", "20:00"
];

let selectedTimeSlot = "10:20";
let currentFilter = 'all';

// Multi-language translation dictionary
const i18n = {
  uz: {
    nav_home: "Bosh sahifa",
    nav_services: "Xizmatlar & Narxlar",
    nav_barbers: "Barberlar",
    nav_book: "Qabulga yozilish",
    nav_contact: "Aloqa",
    hero_title: "Mukammal Uslub, Zamonaviy Parvarish va <span class=\"highlight\">Haqiqiy Erkaklar</span> Muhiti",
    hero_subtitle: "Yangiyo'l shahrining eng zamonaviy erkaklar sartaroshxonasi. 3 nafar mahoratli usta, tasdiqlangan rasmiy narxlar va Telegram bot orqali onlayn qabulga yozilish tizimi.",
    btn_book: "Qabulga yozilish",
    btn_pros: "Barberlarni ko'rish",
    btn_services: "Xizmatlar & Narxlar",
    sec_services_badge: "RASMIY XIZMATLAR VA NARXLAR",
    sec_services_title: "Erkaklar Parvarishi & Narxlar Ro'yxati",
    sec_services_desc: "Har bir xizmat professional vositalar, sterilizatsiyalangan uskunalar va yuqori gigiyena talablari asosida bajariladi.",
    sec_barbers_badge: "BIZNING JAMOAMIZ",
    sec_barbers_title: "Mahoratli Barberlar",
    sec_barbers_desc: "Har bir usta o'z ishining yetuk mutaxassisi bo'lib, sizga individual yondashuv va mukammal natija taqdim etadi.",
    sec_book_badge: "ONLAYN QABULGA YOZILISH",
    sec_book_title: "Usta, Xizmat va Qulay Vaqtni Tanlang",
    sec_book_desc: "Qabulga yozilish bepul va tez. Tanlagan vaqtingizda sizni kutib olamiz.",
    book_now_for_service: "Yozilish"
  },
  ru: {
    nav_home: "Главная",
    nav_services: "Услуги и Цены",
    nav_barbers: "Барберы",
    nav_book: "Онлайн-запись",
    nav_contact: "Контакты",
    hero_title: "Безупречный Стиль, Профессиональный Уход и <span class=\"highlight\">Мужская</span> Атмосфера",
    hero_subtitle: "Современный мужской салон красоты в Янгиюле. 3 топ-мастера, официальный прейскурант и онлайн-запись с мгновенным оповещением в Telegram-бот.",
    btn_book: "Записаться онлайн",
    btn_pros: "Наши мастера",
    btn_services: "Услуги и цены",
    sec_services_badge: "ОФИЦИАЛЬНЫЙ ПРЕЙСКУРАНТ",
    sec_services_title: "Услуги и Стоимость",
    sec_services_desc: "Каждая процедура выполняется профессиональными средствами с соблюдением идеальной гигиены.",
    sec_barbers_badge: "НАША КОМАНДА",
    sec_barbers_title: "Мастера Барбершопа",
    sec_barbers_desc: "Каждый барбер — опытный профессионал, гарантирующий безупречный результат и внимание к деталям.",
    sec_book_badge: "ОНЛАЙН-ЗАПИСЬ",
    sec_book_title: "Выберите мастера, услугу и удобное время",
    sec_book_desc: "Онлайн-запись бесплатна и займет меньше минуты. Мы ждем вас!",
    book_now_for_service: "Записаться"
  },
  en: {
    nav_home: "Home",
    nav_services: "Services & Rates",
    nav_barbers: "Barbers",
    nav_book: "Book Appointment",
    nav_contact: "Contact",
    hero_title: "Impeccable Style, Bespoke Grooming & <span class=\"highlight\">Masculine</span> Atmosphere",
    hero_subtitle: "Yangiyol's premier grooming studio. 3 master barbers, transparent official rates, and effortless appointment scheduling with real-time Telegram alerts.",
    btn_book: "Book Appointment",
    btn_pros: "Meet the Barbers",
    btn_services: "Services & Rates",
    sec_services_badge: "OFFICIAL PRICE CATALOGUE",
    sec_services_title: "Grooming Services & Rates",
    sec_services_desc: "Every service is delivered with premium cosmetic lines, sterilized instruments, and uncompromising hygiene.",
    sec_barbers_badge: "OUR TALENTS",
    sec_barbers_title: "Master Barbers",
    sec_barbers_desc: "Each resident barber brings certified mastery, precision cuts, and bespoke grooming rituals.",
    sec_book_badge: "ONLINE APPOINTMENT",
    sec_book_title: "Choose Your Barber, Service & Preferred Time",
    sec_book_desc: "Booking is free and takes less than a minute. We look forward to welcoming you.",
    book_now_for_service: "Book Now"
  }
};

let currentLang = 'uz';

// Initialize Everything
document.addEventListener('DOMContentLoaded', () => {
  initStorage();
  renderServices();
  initTimeSlots();
  initDatePicker();
  initBookingForm();
  initLanguageSwitcher();
  initAdminModal();
  initBarberModal();
  initFilterButtons();
});

// Load / Initialize Local Storage
function initStorage() {
  if (!localStorage.getItem('wo_man_services')) {
    localStorage.setItem('wo_man_services', JSON.stringify(DEFAULT_SERVICES));
  }
  if (!localStorage.getItem('wo_man_bookings')) {
    // Demo initial bookings so admin and barbers can see right away
    const demoBookings = [
      {
        id: 'WM-' + Math.floor(1000 + Math.random() * 9000),
        barberId: 'akrom',
        barberName: 'Akrom',
        serviceId: 'soch-soqol',
        serviceName: 'Soch soqol (Kompleks)',
        price: 100000,
        date: new Date().toISOString().split('T')[0],
        time: '14:00',
        customerName: 'Sardor Rahimov',
        customerPhone: '+998901234567',
        notes: 'Fade baland bo\'lsin',
        status: 'pending',
        createdAt: new Date().toLocaleString()
      },
      {
        id: 'WM-' + Math.floor(1000 + Math.random() * 9000),
        barberId: 'axror',
        barberName: 'Axror',
        serviceId: 'detskiy',
        serviceName: 'Detskiy (Bolalar soch turmagi)',
        price: 50000,
        date: new Date().toISOString().split('T')[0],
        time: '16:00',
        customerName: 'Bobur Aliyev',
        customerPhone: '+998939876543',
        notes: 'O\'g\'lim bilan boramiz',
        status: 'confirmed',
        createdAt: new Date().toLocaleString()
      },
      {
        id: 'WM-' + Math.floor(1000 + Math.random() * 9000),
        barberId: 'jamoliddin',
        barberName: 'Jamoliddin',
        serviceId: 'kuyov-obroz',
        serviceName: 'Kuyov obroz (VIP Kompleks)',
        price: 400000,
        date: new Date(Date.now() + 86400000).toISOString().split('T')[0],
        time: '11:00',
        customerName: 'Shoxrux Mirzayev',
        customerPhone: '+998971112233',
        notes: 'Shanba kuni to\'y',
        status: 'confirmed',
        createdAt: new Date().toLocaleString()
      }
    ];
    localStorage.setItem('wo_man_bookings', JSON.stringify(demoBookings));
  }
  if (!localStorage.getItem('wo_man_tg_config')) {
    const defaultTg = {
      bot_token: '',
      admin_chat_id: '',
      akrom_chat_id: '',
      axror_chat_id: '',
      jamoliddin_chat_id: ''
    };
    localStorage.setItem('wo_man_tg_config', JSON.stringify(defaultTg));
  }
}

// Get Services from Storage
function getServices() {
  try {
    return JSON.parse(localStorage.getItem('wo_man_services')) || DEFAULT_SERVICES;
  } catch (e) {
    return DEFAULT_SERVICES;
  }
}

// Render 10 Services in Glassmorphism Cards (NO BOARD IMAGE!)
function renderServices() {
  const container = document.getElementById('services-grid-container');
  if (!container) return;

  const services = getServices();
  const filtered = currentFilter === 'all' 
    ? services 
    : services.filter(s => s.category === currentFilter);

  container.innerHTML = '';
  filtered.forEach(srv => {
    const card = document.createElement('div');
    card.className = `service-glass-card ${srv.category === 'vip' ? 'vip' : ''}`;
    card.innerHTML = `
      <div>
        <div class="service-card-top">
          <div class="service-num-badge">${srv.num}</div>
          <div class="service-duration-badge">⏱ ${srv.duration} daqiqa</div>
        </div>
        <h3 class="service-name">${srv.name}</h3>
        <p class="service-desc">${srv.desc}</p>
      </div>
      <div class="service-card-bottom">
        <div class="service-price-tag">
          ${srv.price.toLocaleString()} <span>UZS</span>
        </div>
        <button type="button" class="btn btn-gold btn-sm btn-select-service" data-service-id="${srv.id}">
          Qabulga yozilish &rarr;
        </button>
      </div>
    `;
    container.appendChild(card);
  });

  // Re-attach click listeners on "Yozilish"
  container.querySelectorAll('.btn-select-service').forEach(btn => {
    btn.addEventListener('click', () => {
      const srvId = btn.dataset.serviceId;
      const select = document.getElementById('book-service');
      if (select && srvId) {
        select.value = srvId;
      }
      const bookingSec = document.getElementById('band-qilish');
      if (bookingSec) {
        bookingSec.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  // Also populate booking select dropdown
  const bookSelect = document.getElementById('book-service');
  if (bookSelect) {
    const currentVal = bookSelect.value;
    bookSelect.innerHTML = services.map(s => 
      `<option value="${s.id}">${s.name} — ${s.price.toLocaleString()} UZS (${s.duration} min)</option>`
    ).join('');
    if (currentVal) bookSelect.value = currentVal;
  }
}

// Category filter buttons
function initFilterButtons() {
  document.querySelectorAll('.filter-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.filter-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentFilter = btn.dataset.filter || 'all';
      renderServices();
    });
  });
}

// Render Time Slots
function initTimeSlots() {
  const container = document.getElementById('time-slots-container');
  if (!container) return;

  container.innerHTML = '';
  TIME_SLOTS.forEach(slot => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'slot-btn' + (slot === selectedTimeSlot ? ' active' : '');
    btn.textContent = slot;
    btn.addEventListener('click', () => {
      document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      selectedTimeSlot = slot;
      const hiddenInput = document.getElementById('selected-time');
      if (hiddenInput) hiddenInput.value = slot;
    });
    container.appendChild(btn);
  });
}

// Date Picker Init
function initDatePicker() {
  const dateInput = document.getElementById('book-date');
  if (dateInput) {
    const today = new Date().toISOString().split('T')[0];
    dateInput.value = today;
    dateInput.min = today;
  }
}

// ==================== TELEGRAM BOT ENGINE ====================

// Send message to Telegram Bot API
async function sendTelegramNotification(token, chatId, text) {
  if (!token || !chatId) {
    return { success: false, message: "Token yoki Chat ID kiritilmagan" };
  }
  try {
    const response = await fetch(`https://api.telegram.org/bot${token.trim()}/sendMessage`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chat_id: String(chatId).trim(),
        text: text,
        parse_mode: 'HTML'
      })
    });
    const data = await response.json();
    if (data.ok) {
      return { success: true, message: "Xabar muvaffaqiyatli yetkazildi!" };
    } else {
      return { success: false, message: data.description || "Telegram API xatoligi" };
    }
  } catch (err) {
    return { success: false, message: "Internet yoki tarmoq xatoligi: " + err.message };
  }
}

// Format message for Telegram
function formatTelegramBookingMessage(booking) {
  return `💈 <b>WO&MAN BARBERSHOP — YANGI BUYURTMA!</b>\n\n` +
         `🆔 <b>Buyurtma kodi:</b> <code>${booking.id}</code>\n` +
         `👤 <b>Mijoz:</b> ${booking.customerName}\n` +
         `📞 <b>Telefon:</b> <a href="tel:${booking.customerPhone}">${booking.customerPhone}</a>\n` +
         `✂️ <b>Xizmat:</b> ${booking.serviceName} (${booking.price.toLocaleString()} UZS)\n` +
         `💈 <b>Tanlangan usta:</b> ${booking.barberName}\n` +
         `📅 <b>Sana va vaqt:</b> ${booking.date} soat ${booking.time}\n` +
         (booking.notes ? `📝 <b>Mijoz istagi:</b> ${booking.notes}\n` : '') +
         `\n🔔 <i>Iltimos, mijoz bilan bog'laning yoki uni belgilangan vaqtda kutib oling.</i>`;
}

// Handle Client Booking Submission
function initBookingForm() {
  const form = document.getElementById('main-booking-form');
  if (!form) return;

  // Barber buttons in cards ("Qabuliga yozilish")
  document.querySelectorAll('.btn-book-barber').forEach(btn => {
    btn.addEventListener('click', () => {
      const barberId = btn.dataset.barber;
      const select = document.getElementById('book-barber');
      if (select && barberId) {
        select.value = barberId;
      }
      const bookingSec = document.getElementById('band-qilish');
      if (bookingSec) {
        bookingSec.scrollIntoView({ behavior: 'smooth' });
      }
    });
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();

    const barberSelect = document.getElementById('book-barber');
    const serviceSelect = document.getElementById('book-service');
    const dateInput = document.getElementById('book-date');
    const nameInput = document.getElementById('book-name');
    const phoneInput = document.getElementById('book-phone');
    const notesInput = document.getElementById('book-notes');

    const barberId = barberSelect.value;
    const barberObj = BARBERS[barberId] || { name: 'Istalgan bo\'sh usta', id: 'any' };

    const services = getServices();
    const serviceObj = services.find(s => s.id === serviceSelect.value) || { name: serviceSelect.options[serviceSelect.selectedIndex].text, price: 0 };

    const newBooking = {
      id: 'WM-' + Math.floor(1000 + Math.random() * 9000),
      barberId: barberId,
      barberName: barberObj.name,
      serviceId: serviceSelect.value,
      serviceName: serviceObj.name,
      price: serviceObj.price || 0,
      date: dateInput.value,
      time: selectedTimeSlot,
      customerName: nameInput.value.trim(),
      customerPhone: phoneInput.value.trim(),
      notes: notesInput ? notesInput.value.trim() : '',
      status: 'pending',
      createdAt: new Date().toLocaleString()
    };

    if (!newBooking.customerName || !newBooking.customerPhone) {
      alert("Iltimos, ismingiz va telefon raqamingizni kiriting!");
      return;
    }

    // Save locally
    const bookings = JSON.parse(localStorage.getItem('wo_man_bookings') || '[]');
    bookings.unshift(newBooking);
    localStorage.setItem('wo_man_bookings', JSON.stringify(bookings));

    // Telegram Bot Notifications
    const tgConfig = JSON.parse(localStorage.getItem('wo_man_tg_config') || '{}');
    let tgStatusInfo = "";

    if (tgConfig.bot_token) {
      const tgText = formatTelegramBookingMessage(newBooking);

      // 1. Send to assigned barber if their chat ID is configured
      const barberChatIdKey = `${barberId}_chat_id`;
      const barberChatId = tgConfig[barberChatIdKey];
      if (barberChatId) {
        sendTelegramNotification(tgConfig.bot_token, barberChatId, tgText);
      }

      // 2. Also send to Admin if admin chat ID is configured
      if (tgConfig.admin_chat_id && tgConfig.admin_chat_id !== barberChatId) {
        sendTelegramNotification(tgConfig.bot_token, tgConfig.admin_chat_id, tgText);
      }

      tgStatusInfo = "✅ Telegram bot orqali usta va adminga xabarnoma jo'natildi!";
    } else {
      tgStatusInfo = "ℹ️ Buyurtma qabul qilindi. Tez orada usta siz bilan bog'lanadi.";
    }

    // Show Confirmation Modal
    showBookingConfirmation(newBooking, tgStatusInfo);
    form.reset();
    initDatePicker();
  });
}

function showBookingConfirmation(booking, tgInfo) {
  const modal = document.getElementById('success-modal');
  const content = document.getElementById('booking-details-content');
  if (!modal || !content) return;

  content.innerHTML = `
    <div style="background: rgba(197, 164, 109, 0.08); border: 1px solid var(--color-border-gold); padding: 1.4rem; border-radius: var(--radius-md); margin-block: 1rem; text-align: left;">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem; border-bottom: 1px solid rgba(255,255,255,0.08); padding-bottom: 0.5rem;">
        <span style="font-weight: 700; color: var(--color-gold);">Buyurtma kodi:</span>
        <code style="background: rgba(0,0,0,0.4); padding: 2px 8px; border-radius: 4px; color: #fff;">${booking.id}</code>
      </div>
      <p style="margin-bottom: 0.4rem;"><strong>Barber:</strong> ${booking.barberName}</p>
      <p style="margin-bottom: 0.4rem;"><strong>Xizmat:</strong> ${booking.serviceName} (${booking.price.toLocaleString()} UZS)</p>
      <p style="margin-bottom: 0.4rem;"><strong>Sana & Vaqt:</strong> ${booking.date} soat ${booking.time}</p>
      <p style="margin-bottom: 0.4rem;"><strong>Mijoz:</strong> ${booking.customerName} (${booking.customerPhone})</p>
      ${booking.notes ? `<p style="margin-bottom: 0.4rem;"><strong>Izoh:</strong> ${booking.notes}</p>` : ''}
      <div style="margin-top: 0.8rem; font-size: 0.85rem; color: #34d399; font-weight: 600;">
        ${tgInfo}
      </div>
    </div>
    <div style="display: flex; gap: 0.8rem; justify-content: center; flex-wrap: wrap;">
      <a href="https://t.me/wo_man_yangiyol" target="_blank" rel="noopener" class="btn btn-glass-neon btn-sm">
        Telegram orqali bog'lanish
      </a>
      <a href="tel:+998979775994" class="btn btn-glass btn-sm">
        Qo'ng'iroq qilish
      </a>
    </div>
  `;

  modal.classList.add('active');
}

// ==================== ADMIN PANEL MODAL ====================

function initAdminModal() {
  const trigger = document.getElementById('open-admin-btn');
  const modal = document.getElementById('admin-modal');
  const closeBtn = document.getElementById('admin-modal-close');

  if (trigger && modal) {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      modal.classList.add('active');
      renderAdminBookings();
      loadAdminTelegramSettings();
      renderAdminServicesTable();
    });
  }

  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => {
      modal.classList.remove('active');
    });
  }

  // Admin Tabs
  document.querySelectorAll('.admin-tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.admin-tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.admin-tab-content').forEach(c => c.style.display = 'none');
      btn.classList.add('active');
      const target = document.getElementById(btn.dataset.target);
      if (target) target.style.display = 'block';
    });
  });

  // Telegram Config Save
  const tgForm = document.getElementById('admin-telegram-form');
  if (tgForm) {
    tgForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const config = {
        bot_token: document.getElementById('tg-bot-token').value.trim(),
        admin_chat_id: document.getElementById('tg-admin-chat-id').value.trim(),
        akrom_chat_id: document.getElementById('tg-akrom-chat-id').value.trim(),
        axror_chat_id: document.getElementById('tg-axror-chat-id').value.trim(),
        jamoliddin_chat_id: document.getElementById('tg-jamoliddin-chat-id').value.trim()
      };
      localStorage.setItem('wo_man_tg_config', JSON.stringify(config));
      alert("✅ Telegram bot sozlamalari muvaffaqiyatli saqlandi!");
    });
  }

  // Test Telegram Notification Button
  const testBtn = document.getElementById('btn-test-telegram');
  if (testBtn) {
    testBtn.addEventListener('click', async () => {
      const token = document.getElementById('tg-bot-token').value.trim();
      const chatId = document.getElementById('tg-admin-chat-id').value.trim();
      const feedback = document.getElementById('tg-test-feedback');

      if (!token || !chatId) {
        alert("Iltimos, avval Bot Token va Admin Chat ID ni kiriting!");
        return;
      }

      feedback.innerHTML = `<span style="color: var(--color-gold);">⏳ Telegram orqali sinov xabari yuborilmoqda...</span>`;
      const testMsg = `💈 <b>WO&MAN BARBERSHOP TEST XABARI</b>\n\n` +
                      `✅ Telegram bot ulanishi muvaffaqiyatli amalga oshirildi!\n` +
                      `📅 Vaqt: ${new Date().toLocaleString()}\n` +
                      `Endi barcha buyurtmalar shu yerga va har bir barberga yetkaziladi.`;

      const res = await sendTelegramNotification(token, chatId, testMsg);
      if (res.success) {
        feedback.innerHTML = `<span style="color: #34d399; font-weight: 600;">✅ Telegram bot muvaffaqiyatli ulandi va xabar yetkazildi!</span>`;
      } else {
        feedback.innerHTML = `<span style="color: #f87171; font-weight: 600;">❌ Xatolik: ${res.message}</span>`;
      }
    });
  }
}

function loadAdminTelegramSettings() {
  const config = JSON.parse(localStorage.getItem('wo_man_tg_config') || '{}');
  if (document.getElementById('tg-bot-token')) document.getElementById('tg-bot-token').value = config.bot_token || '';
  if (document.getElementById('tg-admin-chat-id')) document.getElementById('tg-admin-chat-id').value = config.admin_chat_id || '';
  if (document.getElementById('tg-akrom-chat-id')) document.getElementById('tg-akrom-chat-id').value = config.akrom_chat_id || '';
  if (document.getElementById('tg-axror-chat-id')) document.getElementById('tg-axror-chat-id').value = config.axror_chat_id || '';
  if (document.getElementById('tg-jamoliddin-chat-id')) document.getElementById('tg-jamoliddin-chat-id').value = config.jamoliddin_chat_id || '';
}

function renderAdminBookings(filterBarber = 'all') {
  const container = document.getElementById('admin-bookings-table-body');
  if (!container) return;

  const bookings = JSON.parse(localStorage.getItem('wo_man_bookings') || '[]');
  const filtered = filterBarber === 'all' 
    ? bookings 
    : bookings.filter(b => b.barberId === filterBarber);

  if (filtered.length === 0) {
    container.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 2rem; color: var(--color-stone);">Hozircha buyurtmalar yo'q.</td></tr>`;
    return;
  }

  container.innerHTML = filtered.map(b => `
    <tr>
      <td><code>${b.id}</code></td>
      <td><strong>${b.customerName}</strong><br><small><a href="tel:${b.customerPhone}" style="color: var(--color-gold);">${b.customerPhone}</a></small></td>
      <td><span class="badge-glass-gold" style="padding: 2px 8px; font-size: 0.72rem;">${b.barberName}</span></td>
      <td>${b.serviceName}<br><small style="color: var(--color-stone);">${b.price.toLocaleString()} UZS</small></td>
      <td>${b.date}<br><small>${b.time}</small></td>
      <td><span class="status-badge status-${b.status}">${b.status === 'confirmed' ? 'Tasdiqlangan' : b.status === 'cancelled' ? 'Bekor qilingan' : 'Kutilmoqda'}</span></td>
      <td>
        <div style="display: flex; gap: 4px;">
          <button type="button" class="btn btn-glass btn-sm" onclick="changeBookingStatus('${b.id}', 'confirmed')" title="Tasdiqlash" style="color: #34d399; padding: 3px 8px;">✓</button>
          <button type="button" class="btn btn-glass btn-sm" onclick="changeBookingStatus('${b.id}', 'cancelled')" title="Bekor qilish" style="color: #f87171; padding: 3px 8px;">✕</button>
          <button type="button" class="btn btn-glass btn-sm" onclick="deleteBooking('${b.id}')" title="O'chirish" style="color: #9ca3af; padding: 3px 8px;">🗑</button>
        </div>
      </td>
    </tr>
  `).join('');
}

window.changeBookingStatus = function(id, newStatus) {
  const bookings = JSON.parse(localStorage.getItem('wo_man_bookings') || '[]');
  const b = bookings.find(item => item.id === id);
  if (b) {
    b.status = newStatus;
    localStorage.setItem('wo_man_bookings', JSON.stringify(bookings));
    renderAdminBookings();
    if (window.currentActiveBarber) renderBarberCabinet(window.currentActiveBarber);
  }
};

window.deleteBooking = function(id) {
  if (!confirm("Ushbu buyurtmani o'chirishga ishonchingiz komilmi?")) return;
  let bookings = JSON.parse(localStorage.getItem('wo_man_bookings') || '[]');
  bookings = bookings.filter(b => b.id !== id);
  localStorage.setItem('wo_man_bookings', JSON.stringify(bookings));
  renderAdminBookings();
  if (window.currentActiveBarber) renderBarberCabinet(window.currentActiveBarber);
};

// Admin Services Price Editor
function renderAdminServicesTable() {
  const container = document.getElementById('admin-services-table-body');
  if (!container) return;

  const services = getServices();
  container.innerHTML = services.map(s => `
    <tr>
      <td>${s.num}</td>
      <td><strong>${s.name}</strong></td>
      <td>${s.duration} min</td>
      <td>
        <input type="number" step="5000" id="srv-price-${s.id}" value="${s.price}" class="form-input" style="width: 140px; padding: 0.4rem 0.6rem; font-size: 0.85rem;"> UZS
      </td>
      <td>
        <button type="button" class="btn btn-gold btn-sm" onclick="updateServicePrice('${s.id}')">Saqlash</button>
      </td>
    </tr>
  `).join('');
}

window.updateServicePrice = function(srvId) {
  const input = document.getElementById(`srv-price-${srvId}`);
  if (!input) return;
  const newPrice = parseInt(input.value, 10);
  if (isNaN(newPrice) || newPrice < 0) {
    alert("Iltimos, to'g'ri narx kiriting!");
    return;
  }
  const services = getServices();
  const srv = services.find(s => s.id === srvId);
  if (srv) {
    srv.price = newPrice;
    localStorage.setItem('wo_man_services', JSON.stringify(services));
    alert(`✅ "${srv.name}" narxi ${newPrice.toLocaleString()} UZS ga yangilandi!`);
    renderServices();
  }
};

// ==================== BARBER CABINET MODAL ====================

function initBarberModal() {
  const trigger = document.getElementById('open-barber-btn');
  const modal = document.getElementById('barber-modal');
  const closeBtn = document.getElementById('barber-modal-close');

  if (trigger && modal) {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      modal.classList.add('active');
      renderBarberCabinet('akrom');
    });
  }

  if (closeBtn && modal) {
    closeBtn.addEventListener('click', () => {
      modal.classList.remove('active');
    });
  }

  // Barber Selector Pill buttons inside modal
  document.querySelectorAll('.barber-select-pill').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.barber-select-pill').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      renderBarberCabinet(btn.dataset.barberId);
    });
  });

  // Barber personal Telegram ID save
  const tgForm = document.getElementById('barber-personal-tg-form');
  if (tgForm) {
    tgForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const barberId = window.currentActiveBarber || 'akrom';
      const chatId = document.getElementById('barber-personal-chat-id').value.trim();
      const config = JSON.parse(localStorage.getItem('wo_man_tg_config') || '{}');
      config[`${barberId}_chat_id`] = chatId;
      localStorage.setItem('wo_man_tg_config', JSON.stringify(config));
      alert(`✅ ${BARBERS[barberId].name} uchun Telegram Chat ID saqlandi! Endi barcha mijozlaringiz xabarlari sizning Telegramingizga keladi.`);
    });
  }
}

function renderBarberCabinet(barberId) {
  window.currentActiveBarber = barberId;
  const barber = BARBERS[barberId];
  if (!barber) return;

  // Header info
  const nameEl = document.getElementById('barber-cab-name');
  const rankEl = document.getElementById('barber-cab-rank');
  const phoneEl = document.getElementById('barber-cab-phone');
  const photoEl = document.getElementById('barber-cab-photo');
  const tgInput = document.getElementById('barber-personal-chat-id');

  if (nameEl) nameEl.textContent = barber.name;
  if (rankEl) rankEl.textContent = barber.rank;
  if (phoneEl) phoneEl.textContent = barber.phone_display;
  if (photoEl) photoEl.src = barber.photo;

  // Telegram Chat ID load for this specific barber
  const config = JSON.parse(localStorage.getItem('wo_man_tg_config') || '{}');
  if (tgInput) tgInput.value = config[`${barberId}_chat_id`] || '';

  // Filter ONLY this barber's bookings!
  const bookings = JSON.parse(localStorage.getItem('wo_man_bookings') || '[]');
  const myBookings = bookings.filter(b => b.barberId === barberId);

  const container = document.getElementById('barber-my-bookings-container');
  if (!container) return;

  if (myBookings.length === 0) {
    container.innerHTML = `
      <div style="text-align: center; padding: 2.5rem; color: var(--color-stone); background: rgba(255,255,255,0.02); border-radius: var(--radius-md);">
        Sizga hozircha yangi buyurtmalar kelib tushmagan.
      </div>
    `;
    return;
  }

  container.innerHTML = myBookings.map(b => `
    <div class="glass-card" style="padding: 1.2rem; margin-bottom: 1rem; border-color: ${b.status === 'confirmed' ? 'rgba(52, 211, 153, 0.4)' : 'rgba(255, 255, 255, 0.12)'};">
      <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.6rem;">
        <div>
          <span style="font-size: 0.75rem; color: var(--color-gold); font-weight: 700;">${b.id}</span>
          <h4 style="font-size: 1.2rem; margin-top: 0.2rem;">${b.customerName}</h4>
        </div>
        <span class="status-badge status-${b.status}">${b.status === 'confirmed' ? 'Qabul qilingan' : b.status === 'cancelled' ? 'Bekor qilingan' : 'Kutilmoqda'}</span>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 0.8rem; font-size: 0.88rem; margin-bottom: 0.8rem; background: rgba(0,0,0,0.25); padding: 0.8rem; border-radius: var(--radius-sm);">
        <div><strong>✂️ Xizmat:</strong> ${b.serviceName}</div>
        <div><strong>💰 Narxi:</strong> ${b.price.toLocaleString()} UZS</div>
        <div><strong>📅 Sana:</strong> ${b.date}</div>
        <div><strong>⏰ Vaqt:</strong> ${b.time}</div>
      </div>

      ${b.notes ? `<div style="font-size: 0.85rem; color: var(--color-stone); margin-bottom: 0.8rem;"><strong>📝 Mijoz istagi:</strong> ${b.notes}</div>` : ''}

      <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.08); padding-top: 0.8rem; flex-wrap: gap: 0.5rem;">
        <div style="display: flex; gap: 0.6rem;">
          <a href="tel:${b.customerPhone}" class="btn btn-gold btn-sm">
            📞 Qo'ng'iroq: ${b.customerPhone}
          </a>
        </div>
        <div style="display: flex; gap: 0.5rem;">
          ${b.status !== 'confirmed' ? `<button type="button" class="btn btn-glass btn-sm" onclick="changeBookingStatus('${b.id}', 'confirmed')" style="color: #34d399;">✓ Qabul qildim</button>` : ''}
          ${b.status !== 'cancelled' ? `<button type="button" class="btn btn-glass btn-sm" onclick="changeBookingStatus('${b.id}', 'cancelled')" style="color: #f87171;">Bekor qilish</button>` : ''}
        </div>
      </div>
    </div>
  `).join('');
}

// ==================== LANGUAGE SWITCHER ====================
function initLanguageSwitcher() {
  document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const lang = btn.dataset.lang;
      if (!lang || lang === currentLang) return;
      document.querySelectorAll('.lang-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      currentLang = lang;
      applyLanguage(lang);
    });
  });
}

function applyLanguage(lang) {
  const t = i18n[lang] || i18n.uz;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.dataset.i18n;
    if (t[key]) el.innerHTML = t[key];
  });
}
