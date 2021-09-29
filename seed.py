from models import User, db
from app import app

# Create all tables
db.drop_all()
db.create_all()

# Populate the pets table with some rows of data 
# user1 = Pet(username='john', password='testing123', email='john@gmail.com', first_name='john', last_name='smith')

# db.session.add_all([user1])
db.session.commit()