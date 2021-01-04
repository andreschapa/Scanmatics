from views import db

class Customer(db.Model):

    __tablename__="customers"
    customer_id =db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    company_id= db.Column(db.String, db.ForeignKey('users.company'))
    projects=db.relationship('Project', backref='customer')


    def __init__(self, name, company_id):
        self.name=name
        self.company_id= company_id

    def __repr__(self):
        return '<name {0}>'.format(self.name)

class User(db.Model):

    __tablename__='users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    company = db.Column(db.String, nullable=False)
    customers=db.relationship('Customer', backref='poster')

    def __init__(self, name=None, email=None, password=None, company=None):
        self.name= name
        self.email=email
        self.password=password
        self.company= company

    def __repr__(self):
        return '<User {0}>'.format(self.name) ##might need to come back and also return company name

class Project(db.Model):

    __tablename__='projects'
    project_id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    project_customer_id=db.Column(db.Integer, db.ForeignKey('customers.customer_id'))

    def __init__(self, name, project_customer_id):
        self.name=name
        self.project_customer_id= project_customer_id
    
    def __repr__(self):
        return '<name {0}>'.format(self.name)
    



