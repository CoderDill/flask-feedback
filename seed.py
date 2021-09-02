from models import User, db, Feedback
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

db.drop_all()
db.create_all()

password = 'pass'

hashed = bcrypt.generate_password_hash(password)
hashed_utf8 = hashed.decode("utf8")

u1 = User(username='Test User', password=hashed_utf8,
          email="coolbeans@test.com", first_name="John", last_name="Smith")
# u2 = User(username='John Smith', password='HotBeans',
#           email="hotbeans@test.com", first_name="Matt", last_name="Ko")

f1 = Feedback(title="Good Job", content="You were very helpful.",
              username=u1.username)

db.session.add_all([u1, f1])
db.session.commit()
