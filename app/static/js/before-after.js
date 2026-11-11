/**
 * WO&MAN — Interactive Before & After Image Comparison Slider
 */
document.addEventListener('DOMContentLoaded', () => {
  const sliders = document.querySelectorAll('.ba-slider-container');

  sliders.forEach(slider => {
    const beforeWrapper = slider.querySelector('.ba-before-wrapper');
    const handle = slider.querySelector('.ba-handle');
    let isDown = false;

    function move(e) {
      if (!isDown) return;
      const rect = slider.getBoundingClientRect();
      const pageX = e.touches ? e.touches[0].clientX : e.clientX;
      let pos = pageX - rect.left;

      if (pos < 0) pos = 0;
      if (pos > rect.width) pos = rect.width;

      const percentage = (pos / rect.width) * 100;
      beforeWrapper.style.width = percentage + '%';
      handle.style.left = percentage + '%';
    }

    slider.addEventListener('mousedown', () => isDown = true);
    window.addEventListener('mouseup', () => isDown = false);
    slider.addEventListener('mousemove', move);

    slider.addEventListener('touchstart', () => isDown = true, { passive: true });
    window.addEventListener('touchend', () => isDown = false);
    slider.addEventListener('touchmove', move, { passive: true });
  });

  // Mobile navigation drawer toggle
  const mobileBtn = document.getElementById('mobile-toggle-btn');
  const mobileDrawer = document.getElementById('mobile-nav-drawer');
  const mobileClose = document.getElementById('mobile-drawer-close');

  if (mobileBtn && mobileDrawer) {
    mobileBtn.addEventListener('click', () => {
      mobileDrawer.style.display = 'block';
    });
  }
  if (mobileClose && mobileDrawer) {
    mobileClose.addEventListener('click', () => {
      mobileDrawer.style.display = 'none';
    });
  }
});
