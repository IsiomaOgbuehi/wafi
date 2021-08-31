from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import DateTime

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    account_balance = db.Column(db.Integer, default=0)
    account_number = db.Column(db.String(120))

    shows = db.relationship(
        'Transaction', backref='transactions_user', lazy=True)
    __table_args__ = (db.UniqueConstraint('email', 'account_number'), )
    
    def __init__(self, name, email, password, account_number):
        self.name = name
        self.email = email
        self.password = password
        self.account_number = account_number

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def format(self):
        return {
            'name': self.name,
            'email': self.email,
            'account_number': self.account_number
        }


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    transfer_type = db.Column(db.String, nullable=False) # Debit or Credit
    transaction_amount = db.Column(db.Integer) # Amount
    transaction_category = db.Column(db.String, nullable=True, default='Self') # P2P, Self, or Outbound
    recipient_account = db.Column(db.String, nullable=False)
    transaction_date = db.Column(DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey(
        'users.id'), nullable=False)
    
    def __init__(self, transfer_type, transaction_amount, transaction_category, recipient_account, user_id):
        self.transfer_type = transfer_type
        self.transaction_amount = transaction_amount
        self.transaction_category = transaction_category
        self.recipient_account = recipient_account
        self.user_id = user_id

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def format(self):
        return {
            'user_id': self.user_id,
            'transaction_amount': self.transaction_amount,
            'recipient_account': self.recipient_account
        }
