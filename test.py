import unittest

from app import bp, db
from app.models import User, Post


class UserModelCase(unittest.TestCase):
    def setUp(self):
        bp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_password_hashing(self):
        user = User(username='test_1', email='1@1.com')
        user.set_password('weiss')
        self.assertFalse(user.check_password(''))
        self.assertFalse(user.check_password('notweiss'))
        self.assertFalse(user.check_password('Weiss'))
        self.assertFalse(user.check_password('weiss'.upper()))
        self.assertTrue(user.check_password('weiss'))

    def test_generate_avatar(self):
        u = User(username='john', email='john@example.com')
        self.assertEqual(u.generate_avatar(128), ('https://www.gravatar.com/avatar/'
                                         'd4c74594d841139328695756648b6bd6'
                                         '?d=identicon&s=128'))
    def test_follow(self):

        user1 = User(username='wiss',email='wiss@bm.io')
        user2 = User(username='ryma',email='rh@bm.io')

        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()

        self.assertEqual(user1.followed.all(),[])
        self.assertEqual(user2.followed.all(),[])
        self.assertFalse(user1.is_following(user2))

        user1.follow(user2)
        self.assertTrue(user1.is_following(user2))
        self.assertFalse(user2.is_following(user1))
        self.assertEqual(user1.followed.count(),1)
        self.assertEqual(user2.followed.count(),0)

        user2.follow(user1)
        user1.unfollow(user2)
        self.assertFalse(user1.is_following(user2))
        self.assertTrue(user2.is_following(user1))
        self.assertEqual(user1.followed.count(),0)

    def test_post_feed(self):
        u1 = User(username='john', email='john@example.com')
        u2 = User(username='susan', email='susan@example.com')
        u3 = User(username='mary', email='mary@example.com')
        u4 = User(username='david', email='david@example.com')
        db.session.add_all([u1, u2, u3, u4])

        p1 = Post(content='post from {}'.format(u1.username),user=u1)
        p2 = Post(content='post from {}'.format(u2.username),user=u2)
        p3 = Post(content='post from {}'.format(u3.username),user=u3)
        p4 = Post(content='post from {}'.format(u4.username),user=u4)

        db.session.add_all([p1,p2,p3,p4])
        db.session.commit()

        u1.follow(u2)
        u1.follow(u4)
        u2.follow(u3)
        u3.follow(u4)

        db.session.commit()

        f1=u1.post_feed().all()
        f2=u2.post_feed().all()
        f3=u3.post_feed().all()
        f4=u4.post_feed().all()


        self.assertEqual(f1, [p2, p4, p1])
        self.assertEqual(f2, [p2, p3])
        self.assertEqual(f3, [p3, p4])
        self.assertEqual(f4, [p4])

if __name__ == '__main__':
    unittest.main(verbosity=2)