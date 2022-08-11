"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        u2 = User.signup('test2', 'email2@email.com', 'password', None)

        db.session.add_all([u1, u2])
        db.session.commit()

        u1 = User.query.get(u1.id)
        u2 = User.query.get(u2.id)

        self.u1 = u1
        self.u2 = u2

        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
    
    def test_user_following(self):
        """Test that the correct user id shows for following and followers"""
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 1)

        self.assertEqual(self.u1.following[0].id, self.u2.id)
        self.assertEqual(self.u2.followers[0].id, self.u1.id)
    
    def test_is_following(self):
        """Test that the correct user appears when following or being followed"""

        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed(self):
        """Test that the correct user is followed by the correct user"""
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    def test_create_user(self):
        u_test = User.signup(email='email3@email.com', username='TestUser', password='password', image_url=None)
        u_test.id = 777

        db.session.add(u_test)
        db.session.commit()

        self.assertEqual(u_test.image_url, "/static/images/default-pic.png")
        self.assertEqual(u_test.id, 777)
        self.assertEqual(u_test.username, 'TestUser')
        self.assertEqual(u_test.email, 'email3@email.com')


    def test_create_user_fail(self):
        test_user = User.signup(None, 'email@email.com', 'password', "/static/images/default-pic.png")
        test_user.id = 787
        db.session.add(test_user)
        with self.assertRaises(exc.IntegrityError) as context: db.session.commit()


    def test_valid_auth(self):
        u = User.authenticate(self.u1.username, 'password')
        self.assertEqual(u.id, self.u1.id)

    def test_invalid_auth(self):
        self.assertFalse(User.authenticate(self.u1.username, 'passw0rd'))
