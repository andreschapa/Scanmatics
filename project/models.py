from views import db

class Customer(db.Model):

    __tablename__="customers"
    customer_id =db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __init__(self, name):
        self.name=name

    def __repr__(self):
        return '<name {0}>'.format(self.name)

    