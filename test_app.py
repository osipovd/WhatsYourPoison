import unittest
from app import app, db
from models import User, FavoriteDrink

class FlaskAppTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Set up the application for testing
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory SQLite database for testing
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing purposes
        app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        cls.client = app.test_client()
        
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        # Clean up after all tests are done
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def setUp(self):
        # Prepare some test data before each test
        with app.app_context():
            user = User(
                first_name="John",
                last_name="Doe",
                dob="1990-01-01",
                address="123 Main St",
                city="Sample City",
                state="SC",
                zip="12345",
                phone_number="1234567890",
                email="john@example.com"
            )
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
            self.test_user = User.query.get(user.id)  # Re-fetch the user to ensure it's properly bound

    def tearDown(self):
        # Remove all data after each test
        with app.app_context():
            db.session.remove()
            db.drop_all()
            db.create_all()

    def test_home_page(self):
        # Test if the home page loads
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)

    def test_user_registration(self):
        # Test registering a new user
        response = self.client.post('/', data={
            'first_name': 'Jane',
            'last_name': 'Doe',
            'dob': '1990-01-01',
            'address': '123 Main St',
            'city': 'Sample City',
            'state': 'SC',
            'zip': '12345',
            'phone_number': '0987654321',
            'email': 'jane@example.com',
            'password': 'password123',
            'confirm_password': 'password123'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your account has been created successfully!', response.data)

    def test_login(self):
        # Test logging in as a registered user
        response = self.client.post('/login', data={
            'email': 'john@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Logged in successfully!', response.data)

    def test_edit_profile(self):
        # Log in first
        self.client.post('/login', data={'email': 'john@example.com', 'password': 'password123'}, follow_redirects=True)
        
        # Test editing the profile
        response = self.client.post('/edit-profile', data={
            'first_name': 'Johnny',
            'last_name': 'Doe',
            'dob': '1990-01-01',
            'address': '456 Main St',
            'city': 'Updated City',
            'state': 'FL',  # Use a valid state code here
            'zip': '54321',
            'phone_number': '1234567890',
            'email': 'john@example.com'
        }, follow_redirects=True)

        # Ensure the response was a successful redirect
        self.assertEqual(response.status_code, 200)

        # Check that the success message is displayed
        self.assertIn(b'Your profile has been updated successfully!', response.data)

        # Optional: Verify that the database was updated
        with app.app_context():
            updated_user = User.query.filter_by(email='john@example.com').first()
            self.assertEqual(updated_user.city, 'Updated City')

    def test_cocktails_by_letter_white_russian(self):
        # Log in first
        self.client.post('/login', data={'email': 'john@example.com', 'password': 'password123'}, follow_redirects=True)

        # Test fetching cocktails by the first letter 'w'
        response = self.client.get('/cocktails-by-letter/w', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Cocktails Starting With "W"', response.data)

        # Check if "White Russian" is in the response
        self.assertIn(b'White Russian', response.data)
    
    def test_filter_by_alcoholic(self):
        # Log in first
        self.client.post('/login', data={'email': 'john@example.com', 'password': 'password123'}, follow_redirects=True)

        # Test filtering by alcoholic drinks
        response = self.client.get('/filter-by-alcoholic/Alcoholic', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Alcoholic Cocktails', response.data)

        # Check that at least one drink is displayed
        self.assertIn(b'class="media-body"', response.data)  # Checks that at least one drink entry is present

    def test_filter_by_non_alcoholic(self):
        # Log in first
        self.client.post('/login', data={'email': 'john@example.com', 'password': 'password123'}, follow_redirects=True)

        # Test filtering by non-alcoholic drinks
        response = self.client.get('/filter-by-alcoholic/Non_Alcoholic', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Non Alcoholic Cocktails', response.data)

        # Check if at least one known non-alcoholic drink is present
        self.assertIn(b'Afterglow', response.data)  # Replace with a known drink from the data

    def test_delete_account(self):
        # Log in first
        self.client.post('/login', data={'email': 'john@example.com', 'password': 'password123'}, follow_redirects=True)

        # Test deleting the account
        response = self.client.post('/delete-account', data={'password': 'password123'}, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your account has been deleted successfully.', response.data)

    def test_search_drink_results(self):
        # Log in first
        self.client.post('/login', data={'email': 'john@example.com', 'password': 'password123'}, follow_redirects=True)

        # Test drink search
        response = self.client.get('/search-drink-results?drink_name=Margarita', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Margarita', response.data)
        
    def test_add_favorite_drink(self):
        # Log in as the test user
        self.client.post('/login', data={'email': 'john@example.com', 'password': 'password123'}, follow_redirects=True)

        # Add a favorite drink
        response = self.client.post('/add-favorite/11007', data={
            'drink_name': 'Margarita',
            'drink_thumb': 'https://www.thecocktaildb.com/images/media/drink/wpxpvu1439905379.jpg'
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'{"success":true}', response.data)  # Adjust to match the actual JSON response

        # Verify the favorite drink is saved in the database
        with app.app_context():
            favorite = FavoriteDrink.query.filter_by(user_id=self.test_user.id, drink_id='11007').first()
            self.assertIsNotNone(favorite)

    def test_view_favorites(self):
        # Log in as the test user
        self.client.post('/login', data={'email': 'john@example.com', 'password': 'password123'}, follow_redirects=True)

        # Add a favorite drink manually
        with app.app_context():
            favorite = FavoriteDrink(user_id=self.test_user.id, drink_name='Margarita', drink_id='11007', drink_thumb='https://www.thecocktaildb.com/images/media/drink/wpxpvu1439905379.jpg')
            db.session.add(favorite)
            db.session.commit()

        # View the favorites page
        response = self.client.get('/favorites')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Margarita', response.data)

    def test_remove_favorite(self):
        # Log in as the test user
        self.client.post('/login', data={'email': 'john@example.com', 'password': 'password123'}, follow_redirects=True)

        # Add a favorite drink manually
        with app.app_context():
            favorite = FavoriteDrink(user_id=self.test_user.id, drink_name='Margarita', drink_id='11007', drink_thumb='https://www.thecocktaildb.com/images/media/drink/wpxpvu1439905379.jpg')
            db.session.add(favorite)
            db.session.commit()
            favorite_id = favorite.id

        # Remove the favorite drink
        response = self.client.post(f'/remove-favorite/{favorite_id}')
        self.assertEqual(response.status_code, 200)

        # Parse JSON response and check the success field
        response_data = response.get_json()
        self.assertTrue(response_data.get("success"))
        self.assertEqual(response_data.get("favorite_id"), favorite_id)

        # Verify the favorite drink is removed from the database
        with app.app_context():
            favorite = FavoriteDrink.query.filter_by(id=favorite_id).first()
            self.assertIsNone(favorite)

if __name__ == "__main__":
    unittest.main()


