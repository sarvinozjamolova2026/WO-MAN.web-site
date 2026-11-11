import pytest
from app import create_app
from app.config import TestConfig
from app.models import db, User, Professional, Service, WeeklySchedule, Appointment

@pytest.fixture
def app():
    app = create_app(TestConfig)
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def runner(app):
    return app.test_cli_runner()
