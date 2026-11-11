from app.models import Professional, Service, ServiceCategory

def test_exactly_five_professionals_seeded(app):
    with app.app_context():
        pros = Professional.query.all()
        assert len(pros) == 3, f"Expected 3 barbers, found {len(pros)}"
        
        expected_names = [
            "Akrom",
            "Axror",
            "Jamoliddin"
        ]
        pro_names = [p.name for p in pros]
        for name in expected_names:
            assert name in pro_names, f"Missing barber: {name}"

def test_each_professional_has_independent_portfolio_and_schedule(app):
    with app.app_context():
        pros = Professional.query.all()
        for pro in pros:
            assert pro.slug is not None
            assert pro.photo_url is not None
            assert len(pro.title_uz) > 0
            assert len(pro.bio_uz) > 0
            
            # Independent schedule check (7 days of week configured)
            schedules = pro.schedules.all()
            assert len(schedules) == 7, f"Barber {pro.name} has {len(schedules)} schedule entries"
            
            # Independent portfolio items
            portfolio = pro.portfolio_items.all()
            assert len(portfolio) > 0, f"Barber {pro.name} has no portfolio items"

def test_public_pages_load_successfully(client):
    # Home
    res_home = client.get('/')
    assert res_home.status_code == 200
    assert b"WO&amp;MAN" in res_home.data or b"WO&MAN" in res_home.data
    
    # Services
    res_srv = client.get('/services')
    assert res_srv.status_code == 200
    assert b"Xizmatlar" in res_srv.data
    
    # The 3 Professionals
    res_pros = client.get('/professionals')
    assert res_pros.status_code == 200
    assert b"Akrom" in res_pros.data
    assert b"Axror" in res_pros.data
    assert b"Jamoliddin" in res_pros.data
    
    # Individual professional page
    res_akrom = client.get('/professionals/akrom')
    assert res_akrom.status_code == 200
    assert b"Akrom" in res_akrom.data
    
    # Portfolio page
    res_port = client.get('/portfolio')
    assert res_port.status_code == 200
    
    # Contact page
    res_contact = client.get('/contact')
    assert res_contact.status_code == 200
