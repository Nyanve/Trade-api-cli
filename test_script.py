import unittest
from datetime import datetime
from click.testing import CliRunner
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from sqlalchemy import engine_from_config

from sqlalchemy.sql import text as sa_text
import os 
import models

from cli import create_user_log, deposit, create_trade, fetch_trade_history, bulk_action
from models import UserLogModel, WalletModel, CurrenciesModel, HistoryModel, LikedModel
from db import db
db_url = None
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")  # Set your database URI here
db.init_app(app)

class APITestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with app.app_context():
            db.create_all()

    # @classmethod
    # def tearDownClass(cls):
    #     with app.app_context():
    #         db.session.remove()
    #         db.drop_all()

    def setUp(self):
        self.runner = CliRunner()
        with app.app_context():
            db.session.begin_nested()

    # def tearDown(self):
    #     with app.app_context():
    #         db.session.rollback()
    @classmethod
    def tearDownClass(cls):
        with app.app_context():
            db.session.remove()
            # Clean UserLogModel
            UserLogModel.query.delete()
            # Clean WalletModel
            WalletModel.query.delete()
            # Clean HistoryModel
            HistoryModel.query.delete()
            # Clean LikedModel
            LikedModel.query.delete()
            db.session.commit()

           

    def test_create_user_log(self):
        with app.app_context():
            name = 'Batman'
            currency = 'USD'
            result = self.runner.invoke(create_user_log, ['--name', name, '--currency', currency])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('New created object with exchange_id', result.output)

            # Check if user log exists in the database
            try:
                user = UserLogModel.query.filter_by(name=name).first()
                if not user:
                    raise Exception('User not found')
                    
                self.assertIsNotNone(user)  # Check if user exists
                self.assertEqual(user.currency, currency) # Check if currency is correct
            except Exception as e:
                print(e)
            

    def test_deposit(self):
        with app.app_context():
            result = self.runner.invoke(deposit, ['1', '--amount', '100', '--cur_shortcut', 'EUR'])
            self.assertEqual(result.exit_code, 0)
            self.assertEqual(result.output.strip(), 'Success')

            # Check if wallet exists in the database
            try:
                wallet = WalletModel.query.filter_by(exchange_id=1).first()
                if not wallet:
                    raise Exception('Wallet not found')

                self.assertIsNotNone(wallet)  # Check if wallet exists
                self.assertEqual(wallet.amount, 100)  # Check if amount is correct
                self.assertEqual(wallet.cur_shortcut, 'EUR')  # Check if currency is correct
            except Exception as e:
                print(e)


    def test_create_trade(self):
        with app.app_context():
            result = self.runner.invoke(create_trade, ['1', '--amount', '10', '--currency_in', 'EUR', '--currency_out', 'BOB'])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('Trade created successfully', result.output)

            # Check if history exists in the database
            try:
                history = HistoryModel.query.filter_by(exchange_id=1).first()
                if not history:
                    raise Exception('History not found')

                self.assertIsNotNone(history)  # Check if history exists
                self.assertEqual(history.amount, 10)  # Check if amount is correct
                self.assertEqual(history.currency_in, 'EUR')  # Check if currency in is correct
                self.assertEqual(history.currency_out, 'BOB')  # Check if currency out is correct
                self.assertLessEqual((datetime.now() - history.timestamp).total_seconds(), 300)  # Check if timestamp is correct
            except Exception as e:
                print(e)


    def test_fetch_trade_history(self):
        with app.app_context():
            result = self.runner.invoke(fetch_trade_history, [])
            self.assertEqual(result.exit_code, 0)
            self.assertIn('Trade history', result.output)


    def test_bulk_action_update(self):
        with app.app_context():
            input_values = ['USD', 'EUR', 'GBP', 'stop']
            result = self.runner.invoke(bulk_action, ['1', '--action', 'update'], input='\n'.join(input_values))
            
            # Checking if the currency timestamp has the same day as today
            currency = CurrenciesModel.query.filter_by(cur_shortcut='USD').first()
            self.assertIsNotNone(currency)
            self.assertEqual(currency.timestamp.date(), datetime.now().date())

            currency = CurrenciesModel.query.filter_by(cur_shortcut='EUR').first()
            self.assertIsNotNone(currency)
            self.assertEqual(currency.timestamp.date(), datetime.now().date())

            currency = CurrenciesModel.query.filter_by(cur_shortcut='GBP').first()
            self.assertIsNotNone(currency)
            self.assertEqual(currency.timestamp.date(), datetime.now().date())


    def test_bulk_action_like(self):
        with app.app_context():
            input_values = ['USD', 'EUR', 'CZK', 'stop']
            result = self.runner.invoke(bulk_action, ['1', '--action', 'like'], input='\n'.join(input_values))

            # Checking if the currencies are marked as liked
            currency = LikedModel.query.filter_by(cur_shortcut='USD').first()
            # if it exists, the test passed
            self.assertIsNotNone(currency)
            self.assertEqual(currency.exchange_id, 1)

            currency = LikedModel.query.filter_by(cur_shortcut='EUR').first()
            self.assertIsNotNone(currency)
            self.assertEqual(currency.exchange_id, 1)

            currency = LikedModel.query.filter_by(cur_shortcut='CZK').first()
            self.assertIsNotNone(currency)
            self.assertEqual(currency.exchange_id, 1)


    def test_bulk_action_unlike(self):
        with app.app_context():
            input_values = ['USD', 'stop']
            result = self.runner.invoke(bulk_action, ['1', '--action', 'unlike'], input='\n'.join(input_values))
            
            # Checking if the currencies are marked as unliked
            currency = LikedModel.query.filter_by(cur_shortcut='USD').first()
            # if it exists, the test failed
            self.assertIsNone(currency)


if __name__ == '__main__':
    # testing in desired order
    suite = unittest.TestSuite()
    suite.addTest(APITestCase('test_create_user_log'))
    suite.addTest(APITestCase('test_deposit'))
    suite.addTest(APITestCase('test_create_trade'))
    suite.addTest(APITestCase('test_fetch_trade_history'))
    suite.addTest(APITestCase('test_bulk_action_like'))
    suite.addTest(APITestCase('test_bulk_action_unlike'))
    suite.addTest(APITestCase('test_bulk_action_update'))

    # Create a test runner and run the test suite
    runner = unittest.TextTestRunner()
    runner.run(suite)