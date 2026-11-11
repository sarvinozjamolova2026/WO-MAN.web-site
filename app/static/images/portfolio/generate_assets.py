import os

portfolio_dir = os.path.dirname(os.path.abspath(__file__))

def make_portfolio_svg(filename, title, subtitle, tag, color1, color2, is_before=False):
    accent = '#e07a5f' if is_before else '#C5A46D'
    state_label = 'BEFORE / OLDIN' if is_before else 'AFTER / KEYIN'
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 600" width="100%" height="100%">
  <defs>
    <linearGradient id="pGrad_{filename.replace('.', '_')}" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="{color1}"/>
      <stop offset="100%" stop-color="{color2}"/>
    </linearGradient>
  </defs>
  <rect width="600" height="600" fill="url(#pGrad_{filename.replace('.', '_')})"/>
  <rect x="30" y="30" width="540" height="540" fill="none" stroke="{accent}" stroke-width="1.5" stroke-opacity="0.4" rx="4"/>
  
  <path d="M 100 450 Q 300 200 500 450" stroke="{accent}" stroke-width="2" stroke-opacity="0.2" fill="none"/>
  <circle cx="300" cy="260" r="130" fill="{accent}" fill-opacity="0.07"/>
  
  <rect x="50" y="50" width="150" height="32" rx="16" fill="#111111" fill-opacity="0.85" stroke="{accent}" stroke-width="1"/>
  <text x="125" y="71" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-size="11" font-weight="600" fill="{accent}" letter-spacing="1.5">{state_label}</text>
  
  <text x="540" y="72" text-anchor="end" font-family="'Plus Jakarta Sans', sans-serif" font-size="11" font-weight="500" fill="#888888" letter-spacing="2">{tag}</text>
  
  <text x="50" y="500" font-family="'Playfair Display', Georgia, serif" font-size="24" font-weight="600" fill="#F5F0E8" letter-spacing="0.5">{title}</text>
  <text x="50" y="530" font-family="'Plus Jakarta Sans', sans-serif" font-size="13" font-weight="400" fill="#bbbbbb" letter-spacing="1">{subtitle}</text>
</svg>"""
    with open(os.path.join(portfolio_dir, filename), 'w', encoding='utf-8') as f:
        f.write(svg)

# Generate Before & After pairs
make_portfolio_svg('work-1-before.svg', 'Soqol va soch holati (Oldin)', 'Dastlabki shakl va konturlar', 'BARBERING', '#1f1614', '#120f0e', True)
make_portfolio_svg('work-1-after.svg', 'Low Fade & Royal Beard Shaping', 'Aziz Karimov mualliflik ishi', 'BARBERING', '#181818', '#0c0c0c', False)
make_portfolio_svg('work-1-detail.svg', 'Ustara bilan tozalangan kontur', 'Benuqson geometriya', 'DETAILS', '#1c1c1f', '#0f0f12', False)

make_portfolio_svg('work-2-before.svg', 'Bir xil to‘q rang (Oldin)', 'Bo‘yashdan oldingi holat', 'COLOR ART', '#1e1416', '#100b0c', True)
make_portfolio_svg('work-2-after.svg', 'AirTouch Couture & Balayage', 'Kamila Rahimova mualliflik ishi', 'COLOR ART', '#1d1716', '#0d0b0a', False)
make_portfolio_svg('work-2-detail.svg', 'O‘tish chiziqlari mikro-teksturasi', 'Tabiiy quyosh jilosi', 'DETAILS', '#1e191b', '#0e0b0d', False)

make_portfolio_svg('work-3-before.svg', 'O‘sgan soch shakli (Oldin)', 'Klassik qaychi ishlovidan oldin', 'PRECISION', '#181b18', '#0d100d', True)
make_portfolio_svg('work-3-after.svg', 'Executive Scissor Taper', 'Jamshid Aliev mualliflik ishi', 'PRECISION', '#161917', '#0b0d0c', False)
make_portfolio_svg('work-3-detail.svg', 'Klassik biznes uslubi', 'Kundalik oson stilizatsiya', 'DETAILS', '#191b1a', '#0c0e0d', False)

make_portfolio_svg('work-4-before.svg', 'Quruq va shikastlangan soch (Oldin)', 'Intensiv tiklashdan oldin', 'TRICHOLOGY', '#1d1519', '#100b0d', True)
make_portfolio_svg('work-4-after.svg', 'Molekulyar soch botoksi & Bob', 'Madina Yusupova mualliflik ishi', 'TRICHOLOGY', '#191519', '#0c0a0c', False)
make_portfolio_svg('work-4-detail.svg', 'Ipakdek mayinlik va jilo', 'K18 & Keratin himoyasi', 'DETAILS', '#1b161b', '#0d0a0d', False)

make_portfolio_svg('work-5-before.svg', 'Shaklsiz soch turmagi (Oldin)', 'Tekstura berishdan oldin', 'STYLING', '#15171d', '#0a0c10', True)
make_portfolio_svg('work-5-after.svg', 'Contemporary Textured Crop', 'Shavkat Rustamov mualliflik ishi', 'STYLING', '#13151b', '#090a0d', False)
make_portfolio_svg('work-5-detail.svg', 'Yuz terisi ekspress parvarishi', 'Tozalangan terisi va yangi jilo', 'DETAILS', '#141720', '#0a0c12', False)

services_svgs = [
    ('men-cut-1.svg', "Signature Men's Haircut", 'Erkaklar soch turmagi', '#181818', '#0c0c0c'),
    ('men-cut-2.svg', 'Royal Gentleman Combo', 'Soch + Soqol + Spa', '#1a1918', '#0d0c0b'),
    ('beard-1.svg', 'Beard Sculpting Ritual', 'Soqol dizayni', '#181615', '#0c0a09'),
    ('women-cut-1.svg', 'Master Haircut & Blowdry', 'Ayollar soch turmagi', '#19171b', '#0c0a0e'),
    ('color-1.svg', 'AirTouch & Balayage', 'Murakkab rang berish', '#1a1715', '#0c0b0a'),
    ('treatment-1.svg', 'Molecular Hair Botox', 'Soch botoksi va tiklash', '#1b1619', '#0d0a0c'),
    ('spa-1.svg', 'Scalp Detox & Head Spa', 'Yapon bosh spa rituali', '#151918', '#090d0c'),
    ('spa-2.svg', 'Express Glow Facial', 'Ekspress yuz parvarishi', '#16181e', '#090a10')
]
for fname, title, sub, c1, c2 in services_svgs:
    make_portfolio_svg(fname, title, sub, 'WO&MAN SERVICE', c1, c2, False)

studio_svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 800" width="100%" height="100%">
  <defs>
    <linearGradient id="sGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#181818"/>
      <stop offset="50%" stop-color="#111111"/>
      <stop offset="100%" stop-color="#080808"/>
    </linearGradient>
    <radialGradient id="warmLight" cx="50%" cy="20%" r="60%">
      <stop offset="0%" stop-color="#C5A46D" stop-opacity="0.25"/>
      <stop offset="100%" stop-color="#000000" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect width="1200" height="800" fill="url(#sGrad)"/>
  <rect width="1200" height="800" fill="url(#warmLight)"/>
  <line x1="200" y1="0" x2="200" y2="800" stroke="#252525" stroke-width="2"/>
  <line x1="1000" y1="0" x2="1000" y2="800" stroke="#252525" stroke-width="2"/>
  <rect x="350" y="150" width="500" height="450" rx="250" fill="none" stroke="#C5A46D" stroke-width="1.5" stroke-opacity="0.3"/>
  <circle cx="600" cy="375" r="160" fill="none" stroke="#C5A46D" stroke-width="1" stroke-opacity="0.2"/>
  <text x="600" y="370" text-anchor="middle" font-family="'Playfair Display', Georgia, serif" font-size="42" font-weight="600" fill="#F5F0E8" letter-spacing="4">WO&amp;MAN</text>
  <text x="600" y="410" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-size="14" font-weight="500" fill="#C5A46D" letter-spacing="6">ATELIER &amp; GROOMING SUITE</text>
  <text x="600" y="720" text-anchor="middle" font-family="'Plus Jakarta Sans', sans-serif" font-size="13" font-weight="400" fill="#666666" letter-spacing="3">TOSHKENT • AMIR TEMUR 45</text>
</svg>'''
with open(os.path.join(portfolio_dir, 'studio-interior.svg'), 'w', encoding='utf-8') as f:
    f.write(studio_svg)

print('Portfolio artwork generation complete.')
