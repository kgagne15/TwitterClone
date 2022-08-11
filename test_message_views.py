"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase
from sqlalchemy import orm, exc

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)


        db.session.commit()

    def test_add_message(self):
        """Can use add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")
    
    def test_add_no_session(self):
        with self.client as c:
            resp = c.post('/messages/new', data={'text': 'Hello'})
            self.assertEqual(resp.status_code, 302)
            
            
            with self.assertRaises(orm.exc.NoResultFound) as context:
                Message.query.one()

             
    def test_delete_msg_logged_in(self):
        with self.client as c: 
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            msg = Message(
                text="TEST TEST TEST",
                user_id=self.testuser.id,
                timestamp=None
            )
            db.session.add(msg)
            db.session.commit()
            msg.id = 999

            resp = c.post('/messages/999/delete')
            self.assertEqual(resp.status_code, 302)
            self.assertIsNone(Message.query.get(msg.id))
    
    def test_delete_msg_logged_out(self):
        with self.client as c: 
            
            msg = Message(
                text="TEST TEST TEST",
                user_id=self.testuser.id,
                timestamp=None
            )
            db.session.add(msg)
            db.session.commit()
            msg.id = 999

            resp = c.post('/messages/999/delete')
            self.assertEqual(resp.status_code, 302)
            self.assertEqual(msg.text, 'TEST TEST TEST')
            self.assertIsNotNone(Message.query.get(msg.id))
            
