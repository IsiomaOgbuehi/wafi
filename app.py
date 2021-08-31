from flask import Flask, render_template, request, redirect, url_for, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from models import db, User, Transaction

# TODO: connect to a local postgresql database
# db = SQLAlchemy(app)
# migrate = Migrate(app, db)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, 
                instance_relative_config=True)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    # app.config.from_mapping(
    #     SECRET_KEY='dev',
    #     DATABASE=os.path.join(app.instance_path, 'wafi.sqlite'),
    # )
    
    

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    db.init_app(app)
    migrate = Migrate(app, db)

    # a simple page that says hello
    @app.route('/')
    def index():
        return render_template('pages/index.html')
    '''
        REGISTER USER
    '''
    @app.route('/register', methods=['GET', 'POST'])
    def registerUser():
        method = request.method
        if(method == 'GET'):
            return render_template('pages/register.html')
        if(method == 'POST'):
            data = request.get_json()
            try:
                name = data.get('name')
                email = data.get('email')
                account = data.get('account_number')
                password = data.get('password')
                
                if not name or not email or not account or not password:
                    return jsonify({
                        'success': False,
                        'message': 'required fields expected'
                    }), 412
                else:
                    check_user = db.session.query(
                        User).filter_by(email=email).first()
                    if check_user:
                        return jsonify({
                            'success': False,
                            'message': 'User Already Exists'
                        })
                        
                    user = User(name=name, email=email, account_number=account, password=password)
                    user.insert()
                    return jsonify({
                        'success': True,
                        'email': email,
                        'message': 'User created'
                    })
            except Exception as e:
                return jsonify({
                    'message': e
                }), 422
                
                
    '''
        DEPOSITE MONEY
    '''           
    @app.route('/deposit', methods=['GET', 'POST'])
    def depositMoney():
        method = request.method
        if(method == 'GET'):
            return render_template('pages/deposit.html')
        if(method == 'POST'):
            data = request.get_json()
            email = data.get('email')
            amount = data.get('amount')
            try:
                registered_user = db.session.query(
                    User).filter_by(email=email).first()
                # print(user[0]);
                if (registered_user):
                    registered_user.account_balance = registered_user.account_balance + int(amount)
                    try:
                        registered_user.update()
                        transaction = Transaction(transfer_type='Credit', 
                                                  transaction_amount=amount, 
                                                  transaction_category='Self', 
                                                  recipient_account=registered_user.account_number,
                                                  user_id=registered_user.id)
                        transaction.insert()
                        return jsonify({
                            'message': 'Deposit Successful',
                            'balance': registered_user.account_balance,
                            'success': True,
                            'email': registered_user.email
                        })
                    except Exception as e:
                        return jsonify({
                            'message': e
                        }), 412
            
            except Exception as e:
                return jsonify({
                    'message': e
                }), 404
                
                
    '''
        TRANSFER MONEY
    '''            
    @app.route('/transfer', methods=['GET', 'POST'])
    def transferMoney():
        method = request.method
        if(method == 'GET'):
            return render_template('pages/transfer.html')
        
        if(method == 'POST'):
            data = request.get_json()
            email = data.get('email')
            amount = int(data.get('amount'))
            recipient_account = data.get('recipient_account')
            
            if not email or not amount or not recipient_account:
                return jsonify({
                    'message': 'Required Fields must be filled',
                    'success': False
                }), 412
            
            try:
                sending_user = db.session.query(
                    User).filter_by(email=email).first()
                
                if(sending_user.account_balance < amount):
                    return jsonify({
                        'success': False,
                        'message': 'Insufficient Account Balance'
                    }), 412
                    
                else:
                    try:
                        recipient_user = db.session.query(
                            User).filter_by(account_number=recipient_account).first()
                        
                        if(recipient_user):
                            recipient_user.account_balance = recipient_user.account_balance + amount
                            sending_user.account_balance = sending_user.account_balance - amount
                            sending_user.update()
                            recipient_user.update()
                            transaction = Transaction(transfer_type='Debit',
                                                      transaction_amount=amount,
                                                      transaction_category='P2P',
                                                      recipient_account=recipient_user.account_number,
                                                      user_id=sending_user.id)
                            transaction.insert()
                            return jsonify({
                                'message': 'Transfer Completed',
                                'balance': sending_user.account_balance,
                                'recipient_account': recipient_account,
                                'success': True
                                })
                            
                        else:
                            return jsonify({
                                'message': 'Recipient Not Found',
                                'success': False
                            }), 404
                    except Exception as e:
                        return jsonify({
                            'message': e
                        }), 404
                        
            except Exception as e:
                return jsonify({
                    'message': e
                }), 404
                
    
    '''
        CHECK ACCOUNT BALANCE
    '''            
    @app.route('/balance', methods=['GET', 'POST'])
    def accountBalance():
        method = request.method
        if(method == 'GET'):
            return render_template('pages/balance.html')
        
        if(method == 'POST'):
            data = request.get_json()
            account_number = data.get('account_number')
            if not account_number:
                return jsonify({
                    'success': False,
                    'message': 'User Account Number is required'
                })
            try:
                user = db.session.query(
                    User).filter_by(account_number=account_number).first()
                print(user.account_balance)
                    
                return jsonify({
                    'success': True,
                    'balance': user.account_balance
                })
                    
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': 'User Not Found'
                }), 404
            
    '''
        HANDLE APP ERRORS
    '''

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(412)
    def precondition_failed(error):
        return jsonify({
            'success': False,
            'error': 412,
            'message': 'precondition failed'
        }), 412

    @app.errorhandler(422)
    def unprocessed_request(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessed request'
        }), 422

    return app
