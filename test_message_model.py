"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

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



class MessageModelTestCase(TestCase):

    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u1 = User.signup("test1", "email1@email.com", "password", None)
        


        db.session.add(u1)
        db.session.commit()

        m1 = Message(text="Test Message", timestamp=None, user_id=u1.id)
        db.session.add(m1)
        db.session.commit()

        u1 = User.query.get(u1.id)
        m1 = Message.query.get(m1.id)

        self.u1 = u1
        self.m1 = m1

        self.client = app.test_client()
    
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_message_model(self): 
        """Does basic model work?"""
        m = Message(
            text="TEST TEST TEST",
            user_id=self.u1.id,
            timestamp=None
        )
        db.session.add(m)
        db.session.commit()
        self.assertEqual(m.user_id, self.u1.id)
        self.assertEqual(m.text, 'TEST TEST TEST')
    

    def test_invalid_msg(self):
        msg = Message(text="Test Message", timestamp=None, user_id=None)
        db.session.add(msg)
        with self.assertRaises(exc.IntegrityError) as context: db.session.commit()

    def test_num_msg(self):
        self.assertEqual(len(self.u1.messages), 1)
        self.assertNotEqual(len(self.u1.messages), 34)
    
    def test_msg_likes(self):
        self.u1.likes.append(self.m1)
        db.session.commit()

        l = Likes.query.filter(Likes.user_id == self.u1.id).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, self.m1.id)