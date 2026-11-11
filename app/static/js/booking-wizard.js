/**
 * WO&MAN — Booking Wizard & Real-Time Availability Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  const wizard = document.getElementById('booking-wizard-app');
  if (!wizard) return;

  // State
  let state = {
    step: 1,
    professionalId: wizard.dataset.preselectPro ? parseInt(wizard.dataset.preselectPro) : null,
    professionalName: '',
    serviceId: wizard.dataset.preselectService ? parseInt(wizard.dataset.preselectService) : null,
    serviceName: '',
    serviceDuration: 45,
    servicePrice: 0,
    date: new Date().toISOString().split('T')[0],
    timeStart: '',
    timeEnd: '',
    clientName: '',
    clientPhone: '',
    clientEmail: '',
    clientNote: '',
    consent: false
  };

  const steps = [1, 2, 3, 4, 5];
  
  // Elements
  const stepContainers = document.querySelectorAll('.wizard-step-pane');
  const stepIndicators = document.querySelectorAll('.step-item');
  const slotsContainer = document.getElementById('slots-grid');
  const slotsLoading = document.getElementById('slots-loading');
  const slotsEmpty = document.getElementById('slots-empty');
  const dateInput = document.getElementById('booking-date-input');
  
  // Set min date to today
  if (dateInput) {
    const todayStr = new Date().toISOString().split('T')[0];
    dateInput.min = todayStr;
    dateInput.value = state.date;
    dateInput.addEventListener('change', (e) => {
      state.date = e.target.value;
      loadAvailableSlots();
    });
  }

  // Preselection setup
  if (state.professionalId) {
    const selectedProCard = document.querySelector(`.pro-select-card[data-id="${state.professionalId}"]`);
    if (selectedProCard) {
      selectedProCard.classList.add('selected');
      state.professionalName = selectedProCard.dataset.name;
    }
  }

  // Pro Selection
  document.querySelectorAll('.pro-select-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.pro-select-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      state.professionalId = parseInt(card.dataset.id);
      state.professionalName = card.dataset.name;
      goToStep(2);
    });
  });

  // Service Selection
  document.querySelectorAll('.service-select-card').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.service-select-card').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      state.serviceId = parseInt(card.dataset.id);
      state.serviceName = card.dataset.name;
      state.serviceDuration = parseInt(card.dataset.duration);
      state.servicePrice = parseInt(card.dataset.price);
      goToStep(3);
      loadAvailableSlots();
    });
  });

  // Service Filter Buttons
  document.querySelectorAll('.srv-filter-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.srv-filter-btn').forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const category = btn.dataset.category;
      document.querySelectorAll('.service-select-card').forEach(card => {
        if (category === 'all' || card.dataset.audience === category || card.dataset.category === category) {
          card.style.display = 'flex';
        } else {
          card.style.display = 'none';
        }
      });
    });
  });

  // Fetch Available Slots
  async function loadAvailableSlots() {
    if (!state.professionalId || !state.serviceId || !state.date) return;
    
    slotsLoading.style.display = 'block';
    slotsContainer.innerHTML = '';
    slotsEmpty.style.display = 'none';

    try {
      const res = await fetch(`/api/availability?pro_id=${state.professionalId}&service_id=${state.serviceId}&date=${state.date}`);
      const data = await res.json();
      slotsLoading.style.display = 'none';

      if (data.slots && data.slots.length > 0) {
        data.slots.forEach(slot => {
          const btn = document.createElement('button');
          btn.type = 'button';
          btn.className = 'slot-pill';
          btn.textContent = slot.label;
          if (state.timeStart === slot.start_time) {
            btn.classList.add('selected');
          }
          btn.addEventListener('click', () => {
            document.querySelectorAll('.slot-pill').forEach(s => s.classList.remove('selected'));
            btn.classList.add('selected');
            state.timeStart = slot.start_time;
            state.timeEnd = slot.end_time;
            document.getElementById('btn-step3-next').disabled = false;
          });
          slotsContainer.appendChild(btn);
        });
      } else {
        slotsEmpty.style.display = 'block';
        document.getElementById('btn-step3-next').disabled = true;
      }
    } catch (err) {
      slotsLoading.style.display = 'none';
      slotsEmpty.textContent = 'Xatolik yuz berdi. Iltimos qaytadan urinib ko‘ring.';
      slotsEmpty.style.display = 'block';
    }
  }

  // Navigation handlers
  window.wizardNext = function(fromStep) {
    if (fromStep === 3) {
      if (!state.timeStart) {
        alert('Iltimos, qulay vaqt oralig‘ini tanlang.');
        return;
      }
      goToStep(4);
    } else if (fromStep === 4) {
      // Validate customer inputs
      const nameInput = document.getElementById('cust-name');
      const phoneInput = document.getElementById('cust-phone');
      const consentInput = document.getElementById('cust-consent');
      
      if (!nameInput.value.trim() || nameInput.value.trim().length < 2) {
        alert('Iltimos, ismingizni to‘liq kiriting.');
        nameInput.focus();
        return;
      }
      if (!phoneInput.value.trim() || phoneInput.value.trim().length < 9) {
        alert('Iltimos, telefon raqamingizni kiriting (+998...)');
        phoneInput.focus();
        return;
      }
      if (!consentInput.checked) {
        alert('Iltimos, shaxsiy ma\'lumotlar qayta ishlanishiga rozilik bildiring.');
        consentInput.focus();
        return;
      }

      state.clientName = nameInput.value.trim();
      state.clientPhone = phoneInput.value.trim();
      state.clientEmail = document.getElementById('cust-email')?.value.trim() || '';
      state.clientNote = document.getElementById('cust-note')?.value.trim() || '';
      state.consent = true;

      populateSummary();
      goToStep(5);
    }
  };

  window.wizardBack = function(toStep) {
    goToStep(toStep);
  };

  function goToStep(targetStep) {
    state.step = targetStep;
    stepContainers.forEach(pane => {
      pane.style.display = parseInt(pane.dataset.step) === targetStep ? 'block' : 'none';
    });
    stepIndicators.forEach(ind => {
      const stepNum = parseInt(ind.dataset.step);
      ind.classList.remove('active', 'completed');
      if (stepNum === targetStep) ind.classList.add('active');
      else if (stepNum < targetStep) ind.classList.add('completed');
    });
    window.scrollTo({ top: wizard.offsetTop - 100, behavior: 'smooth' });
  }

  function populateSummary() {
    document.getElementById('sum-pro').textContent = state.professionalName || 'Istalgan mutaxassis';
    document.getElementById('sum-service').textContent = state.serviceName;
    document.getElementById('sum-datetime').textContent = `${state.date} (${state.timeStart} – ${state.timeEnd})`;
    document.getElementById('sum-duration').textContent = `${state.serviceDuration} daqiqa`;
    document.getElementById('sum-price').textContent = `${state.servicePrice.toLocaleString()} so'm`;
    document.getElementById('sum-client').textContent = state.clientName;
    document.getElementById('sum-phone').textContent = state.clientPhone;
    document.getElementById('sum-note').textContent = state.clientNote || "Ko'rsatilmagan";
  }

  // Final Submit
  const submitBtn = document.getElementById('btn-submit-booking-final');
  if (submitBtn) {
    submitBtn.addEventListener('click', async () => {
      submitBtn.disabled = true;
      submitBtn.innerHTML = '<span>Kutilmoqda...</span>';

      try {
        const payload = {
          professional_id: state.professionalId,
          service_id: state.serviceId,
          appointment_date: state.date,
          start_time: state.timeStart,
          end_time: state.timeEnd,
          customer_name: state.clientName,
          customer_phone: state.clientPhone,
          customer_email: state.clientEmail,
          customer_note: state.clientNote
        };

        const res = await fetch('/api/booking/create', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (res.ok && data.success) {
          window.location.href = `/booking/confirmation/${data.reference_code}`;
        } else {
          submitBtn.disabled = false;
          submitBtn.textContent = 'Yozilishni tasdiqlash';
          alert(data.message || 'Xatolik yuz berdi. Iltimos qaytadan urinib ko‘ring.');
          if (res.status === 409) {
            goToStep(3);
            loadAvailableSlots();
          }
        }
      } catch (err) {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Yozilishni tasdiqlash';
        alert('Server bilan ulanishda xatolik yuz berdi.');
      }
    });
  }
});
