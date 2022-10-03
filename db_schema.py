from flask_sqlalchemy import SQLAlchemy
from werkzeug import security
from flask_login import UserMixin
from datetime import datetime
# create the database interface
db = SQLAlchemy()

# a model of a user for the database
class User(UserMixin, db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(40))
    email = db.Column(db.String(40))
    lastLogin = db.Column(db.DateTime)

    def __init__(self, username, password, email, lastLogin):
        self.username=username
        self.password=password
        self.email=email
        self.lastLogin=lastLogin
# a model of a list for the database

class Bill(db.Model):
    __tablename__='bills'
    id = db.Column(db.Integer, primary_key=True)
    billName = db.Column(db.Text())
    amount = db.Column(db.Float)
    people = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # this ought to be a "foreign key"

    def __init__(self, billName, amount, user_id, people):
        self.billName=billName
        self.user_id=user_id
        self.amount=amount
        self.people=people

# a model of a list item for the database
# it refers to a list
class BillPayees(db.Model):
    __tablename__='payees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    cost = db.Column(db.Float)
    payee_status = db.Column(db.Integer)
    payer_status = db.Column(db.Integer)
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'))
    dateCreated = db.Column(db.DateTime)

    def __init__(self, name,users_id, cost, payee_status, payer_status, bill_id, dateCreated):
        self.name=name
        self.cost=cost
        self.bill_id=bill_id
        self.payee_status=payee_status
        self.payer_status=payer_status
        self.users_id=users_id
        self.dateCreated=dateCreated



# put some data into the tables
def dbinit():
    
    # commit all the changes to the database file
    db.session.commit()
