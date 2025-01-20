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

    def test_register_user(self):
        response = self.app.post('/register', json={  # Updated endpoint
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'User registered successfully!', response.data)

    def test_update_password(self):
        # First, register a user
        self.app.post('/register', json={  # Updated endpoint
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword'
        })

        # Get JWT token for the registered user within the app context
        with app.app_context():
            access_token = create_access_token(identity=1)  # Assuming user ID is 1 for the test

        # Update the password
        response = self.app.put('/user/updatepassword', 
                                 headers={'Authorization': f'Bearer {access_token}'},  # Include token
                                 json={
            'new_password': 'newpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Password updated successfully!', response.data)

    def test_update_user(self):
        # First, register a user
        self.app.post('/register', json={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword'
        })

        # Get JWT token for the registered user within the app context
        with app.app_context():
            access_token = create_access_token(identity=1)  # Assuming user ID is 1 for the test

        # Update the user information
        response = self.app.put('/user/update', 
                                 headers={'Authorization': f'Bearer {access_token}'},  # Include token
                                 json={
            'username': 'updateduser',
            'email': 'updated@example.com'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'{"User updated successfully!"}\n', response.data)

        # Test invalid update (no data)
        response = self.app.put('/user/update', 
                                 headers={'Authorization': f'Bearer {access_token}'},  # Include token
                                 json={})
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'{"Invalid data!"}', response.data)

if __name__ == '__main__':
    unittest.main()
