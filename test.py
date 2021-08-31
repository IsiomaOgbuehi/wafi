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

    def test_empty_db(self):
        rv = self.client().get('/hello')
        data = json.loads(rv.data)
        
        self.assertEqual(rv.status_code, 200)
        self.assertEqual(data['val'], 'Halos')
        
        
    # USER REGISTRATION TEST
    def test_user_registration(self):
        res = self.client().post('/register',
                                 json={'name': 'Maskot Rise', 'password': 'abc', 'account_balance': 0, 'email': 'maskot@test.com', 'account_number': '1234567890'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['email'])
    
    # DEPOSIT MONEY
    def test_deposit_money(self):
        res = self.client().post(
            '/deposit', json={'email': 'maskot@test.com', 'amount': 50})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['email'])
        self.assertTrue(data['balance'])
        
    
    # TRANSFER MONEY
    def test_send_money(self):
        res = self.client().post('/transfer', 
            json={'email': 'maskot@test.com',
                  'amount': 50, 'transfer_type': 'Debit', 'transaction_category': 'P2P',
                  'recipient_account': '1234567890', 'user_id': 1})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['recipient_account'])
        self.assertTrue(data['balance'])
        

    def test_check_account_balance(self):
        res = self.client().post('/balance',
            json={'account_number': '1234567890'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['balance'])


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
