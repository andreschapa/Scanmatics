from views import db
from models import Customer

db.create_all()

db.session.add(Customer("Scanmatics"))

db.session.commit()