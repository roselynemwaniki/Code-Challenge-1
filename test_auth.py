import unittest
from app import app, db
from models import User
from flask_jwt_extended import create_access_token

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_missing_authorization_header(self):
        response = self.app.get('/task')  # Example endpoint that requires authorization
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"msg": "Missing Authorization Header"})

    def test_login(self):
        with app.app_context():
            # Create a user only if it does not already exist
            user = User.query.filter_by(username='testuser').first()
            if not user:
                user = User(username='testuser', email='test@example.com', password='testpassword')
                db.session.add(user)
                db.session.commit()

        response = self.app.post('/login', json={'email': 'test@example.com', 'password': 'testpassword'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)

if __name__ == '__main__':
    unittest.main()
