#from views import db
from project import db, app
import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class Customer(db.Model):

    __tablename__="customers"
    customer_id =db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    company_id= db.Column(db.String, db.ForeignKey('users.company'))
    projects=db.relationship('Project', backref='customer')
    panels=db.relationship('Panel', backref='customers') 

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
    company = db.Column(db.String, nullable=False, unique= True)
    customers=db.relationship('Customer', backref='poster')

    def get_reset_token(self, expires_sec=1800):
        s=Serializer('myprecious', expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s=Serializer('myprecious')
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)


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
    panels=db.relationship('Panel', backref='project')
    


    def __init__(self, name, project_customer_id):
        self.name=name
        self.project_customer_id= project_customer_id
    
    def __repr__(self):
        return '<name {0}>'.format(self.name)
    
class Panel(db.Model):

    __tablename__='panels'
    panel_id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String, nullable=False)
    panel_project_id=db.Column(db.Integer, db.ForeignKey('projects.project_id'))
    panel_project_customer_id=db.Column(db.Integer, db.ForeignKey('customers.customer_id'))
    logs=db.relationship('MaintenanceLogs', backref='logs')
    

    def __init__(self, name, panel_project_id, panel_project_customer_id):
        self.name=name
        self.panel_project_id=panel_project_id
        self.panel_project_customer_id=panel_project_customer_id

    def __repr__(self):
        return '<name {0}>'.format(self.name)
#added 1/20
class QRcode(db.Model):
    __tablename__='QRcodes'
    panel_id=db.Column(db.Integer, unique=True)
    end_user=db.Column(db.String, nullable=False)
    panel_name=db.Column(db.String, nullable=False)
    QR_id=db.Column(db.Integer, primary_key=True)

    def __init__(self, panel_id=None, end_user=None, panel_name=None, QR_id=None):
        self.panel_id=panel_id
        self.end_user=end_user
        self.panel_name=panel_name
        self.QR_id=QR_id
       
    
    def __repr__(self):
        return '<name {0}>'.format(self.name)

#Maintenance logs model

class MaintenanceLogs(db.Model):
    __tablename__ = "MaintenanceLogs"
    MaintenanceLog_id = db.Column(db.Integer, primary_key=True)
    MaintenanceLog_panel_id= db.Column(db.Integer, db.ForeignKey('panels.panel_id'))
    maintenance_issue= db.Column(db.String, nullable=False)
    action_taken= db.Column(db.String, nullable=True)
    posted_date = db.Column(db.Date, default=datetime.datetime.utcnow())
    priority = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer)
    

    def __init__(self, maintenance_issue=None, action_taken=None, posted_date=None, priority=None, status=None):
        self.maintenance_issue= maintenance_issue
        self.action_taken = action_taken
        self.posted_date = posted_date
        self.priority= priority
        self.status= status

    def __repr__(self):
        return '<name {0}>'.format(self.name)
    


  


