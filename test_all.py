import unittest
import os
from app import app, db
from models import User, Service, Reservation
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Usuwanie istniejącej bazy danych przed każdym testem
        if os.path.exists('site.db'):
            os.remove('site.db')

        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_user(self):
        # Test tworzenia użytkownika
        with app.app_context():
            user = User(username='testuser', email='test@example.com', password_hash=generate_password_hash('password123'))
            db.session.add(user)
            db.session.commit()

            # Sprawdzenie, czy użytkownik został poprawnie dodany do bazy danych
            queried_user = User.query.filter_by(username='testuser').first()
            self.assertIsNotNone(queried_user)
            self.assertEqual(queried_user.email, 'test@example.com')

    def test_create_service(self):
        # Test tworzenia usługi
        with app.app_context():
            service = Service(name='Test Service', price=100.0, description='Test Description')
            db.session.add(service)
            db.session.commit()

            # Sprawdzenie, czy usługa została poprawnie dodana do bazy danych
            queried_service = Service.query.filter_by(name='Test Service').first()
            self.assertIsNotNone(queried_service)
            self.assertEqual(queried_service.price, 100.0)

    def test_create_reservation(self):
        # Test tworzenia rezerwacji
        with app.app_context():
            user = User(username='testuser', email='test@example.com', password_hash=generate_password_hash('password123'))
            db.session.add(user)
            db.session.commit()

            service = Service(name='Test Service', price=100.0, description='Test Description')
            db.session.add(service)
            db.session.commit()

            reservation = Reservation(
                name='John Doe',
                phone='123456789',
                service_id=service.id,
                start_time=datetime.now(),
                end_time=datetime.now() + timedelta(hours=1),
                user_id=user.id
            )
            db.session.add(reservation)
            db.session.commit()

            # Sprawdzenie, czy rezerwacja została poprawnie dodana do bazy danych
            queried_reservation = Reservation.query.filter_by(name='John Doe').first()
            self.assertIsNotNone(queried_reservation)
            self.assertEqual(queried_reservation.phone, '123456789')

if __name__ == '__main__':
    unittest.main()
