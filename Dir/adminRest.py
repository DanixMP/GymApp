from database import db
# change the password
db.create_user(
    username="admin",
    password="admin@111111",
    full_name="Dev",
    email="admin@gym.com",
    role="admin"
)