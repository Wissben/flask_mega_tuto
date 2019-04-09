from app.models import User,Post
from app import db
from random import randrange


User.query.delete()
users = User.query.all()
start = 0
if users:
    start = users[-1].id

for i in range(start,start+150):
    print('[INFO] : ',i)
    to_add = User(username='user_'+str(i),email='user_'+str(i)+'@dummies.com')
    to_add.set_password(str(i))
    db.session.add(to_add)

db.session.commit()

