import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from app import create_app
from models import User, Transaction

class WafiCase(unittest.TestCase):
    
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client
        # setup_db(self.app)
        
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.client = self.app.test_client
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        pass
        
    # USER REGISTRATION TEST 1234567890
    def test_user_registration(self):
        res = self.client().post('/register',
                                 json={'name': 'New User', 'password': 'abc', 'account_balance': 0, 'email': 'useroio@test.com', 'account_number': '1232188932',
                                       'currency': 'USD'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['data']['email'], 'usero@test.com')
        self.assertEqual(data['data']['name'], 'New User')
        self.assertEqual(data['data']['account_balance'], 0.0)
        self.assertEqual(data['data']['account_number'], '12147688932')
    
    # DEPOSIT MONEY
    def test_deposit_money(self):
        res = self.client().post(
            '/deposit', json={'email': 'useroio@test.com', 'amount': 50})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['email'])
        self.assertTrue(data['balance'])
        
    
    # TRANSFER MONEY
    def test_send_money(self):
        res = self.client().post('/transfer', 
                                 json={'email': 'useroio@test.com',
                  'amount': 50, 'transfer_type': 'Debit', 'transaction_category': 'P2P',
                  'recipient_account': '1232188932', 'user_id': 1})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['recipient_account'], '1232188932')
        self.assertTrue(data['balance'])
        self.assertEqual(data['amount'], 50)
        self.assertEqual(data['email'], 'useroio@test.com')
        
    # CHECK ACCOUNT BALANCE

    def test_check_account_balance(self):
        res = self.client().post('/balance',
            json={'account_number': '1234567890'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['balance'])
        
    
    # ADD CURRENCY
    def test_add_currency(self):
        res = self.client().post('/currency/add', json={
            'currency_type': 'USD', 'currency_value': 1
        })
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['currency'], 'USD')
        self.assertEqual(data['value'], 1.0)
      
    
        


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
