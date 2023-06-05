from flask_smorest import abort
from sqlalchemy.exc import SQLAlchemyError
import json
from datetime import datetime
import requests
import logging


from db import db
from models import UserLogModel
from models import WalletModel
from models import CurrenciesModel
from models import HistoryModel
from schemas import UserLogSchema, WalletSchema


def update_deposit_amount(cur_shortcut, amount, exchange_id):
    existing_wallet = WalletModel.query.filter_by(cur_shortcut=cur_shortcut, exchange_id=exchange_id).first()
    if existing_wallet:
        existing_wallet.amount += amount
    else:
        wallet = WalletModel(cur_shortcut=cur_shortcut, amount=amount, exchange_id=exchange_id)
        db.session.add(wallet)

    db.session.commit()


def check_user_funds(wallet, exchange_id):
    currency_in = wallet.get('currency_in')
    amount = wallet.get('amount')
    existing_wallet = WalletModel.query.filter_by(cur_shortcut=currency_in, exchange_id=exchange_id).first()
    if existing_wallet:
        if existing_wallet.amount >= amount:
            # Create a new trade and add it to the History and update the Wallet funds
            make_trade(wallet, exchange_id)
            # Subtracts used funds 
            logging.info(f'The trade is starting {wallet}')
            existing_wallet.amount -= amount
            db.session.commit()

            # Check if the wallet amount dropped to zero, then delets the funds
            if existing_wallet.amount == 0:
                logging.info(f'The funds droped to zero{wallet}')
                db.session.delete(existing_wallet)
                db.session.commit()
            logging.info('The trade is done successfully')
            calculate_wallet_value(exchange_id)

        else:
            abort(400, message="Not enough funds.")
    else:
        abort(400, message="You dont own enough funds in this currency.")
    

def make_trade(wallet, exchange_id):
    
    logging.info(f'The trade is starting {wallet}')
    # get the walues out of the wallet it is a dict
    currency_in = wallet.get('currency_in')
    currency_out = wallet.get('currency_out')
    amount = wallet.get('amount')

    logging.info(currency_in, currency_out, amount)
    
    # Get the exchange rate from currency_in to EUR
    cur_to_eur = CurrenciesModel.query.filter_by(cur_shortcut=currency_in).first().cur_to_eur
    
    # Calculate the amount in EUR
    amount_eur = amount * cur_to_eur
    logging.info(f'The first trade is done {amount_eur}')
    # Get the exchange rate from EUR to currency_out
    eur_to_cur = CurrenciesModel.query.filter_by(cur_shortcut=currency_out).first().eur_to_cur
    
    # Calculate the amount in currency_out
    amount_out = amount_eur * eur_to_cur
    logging.info(f'The second trade is done {amount_out}')
    

    # Update the Wallet funds
    update_deposit_amount(currency_out, amount_out, exchange_id)
    logging.info('The trade is done successfully')


def populate_currencies_from_json(json_file_path):
    with open(json_file_path, encoding='utf-8') as file:
        data = json.load(file)

    currencies = []

    for currency_code, currency_data in data.items():
        name = currency_data['name']
        code = currency_data['code']
        symbol_native = currency_data['symbol_native']

        currencies.append({
            "cur_name": name,
            'cur_shortcut': code,
            'symbol': symbol_native
        })

    for currency in currencies:
        currency['cur_shortcut'] = CurrenciesModel(
            cur_name=currency['cur_name'],
            cur_shortcut=currency['cur_shortcut'],
            symbol=currency['symbol'],
            cur_to_eur=0.0,  # Set appropriate values
            eur_to_cur=0.0,  # Set appropriate values
            timestamp=datetime.now()  # Set appropriate values
        )
        db.session.add(currency['cur_shortcut'])

    db.session.commit()


def update_currency_rates():
    # API endpoint base URL
    base_url = 'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/'

    # Retrieve currency list with EUR as base currency
    eur_data = requests.get(base_url + 'eur.json').json()
    # Update currency rates in the table

    # Go trought all the currencies in the database and update the rates if needed
    for currency in CurrenciesModel.query.all():
        # check if timsstamp is same as today
        if currency.timestamp.date() == datetime.now().date():
            continue
        
        cur = currency.cur_shortcut.lower()  # Convert currency code to lowercase
        if cur in eur_data['eur']:
            currency.eur_to_cur = eur_data["eur"][cur]  

            # Retrieve currency value for currency to EUR')
            cur_to_eur_data = requests.get(base_url + f'{cur}/eur.json').json()
            currency.cur_to_eur = cur_to_eur_data["eur"]

            # Update the timestamp
            currency.timestamp = datetime.now()
            logging.info(f'Updated currency rates for {cur}') 
            db.session.add(currency)

    # Commit the changes to the database
    db.session.commit()
    return 200


def calculate_wallet_value(exchange_id):
    # go trought all the funds in wallet and 
    # calculate the value of the wallet in EUR
    wallet_value = 0
    for wallet in WalletModel.query.filter_by(exchange_id=exchange_id).all():
        cur = wallet.cur_shortcut
        cur_to_eur = CurrenciesModel.query.filter_by(cur_shortcut=cur).first().cur_to_eur
        wallet_value += wallet.amount * cur_to_eur

    # update the user wallet value
    currency = UserLogModel.query.filter_by(exchange_id=exchange_id).first().currency

    # calculate the value of the wallet in the user chosen currency.
    eur_to_cur = CurrenciesModel.query.filter_by(cur_shortcut=currency).first().eur_to_cur
    wallet_value = wallet_value * eur_to_cur

    # update the user wallet value
    user = UserLogModel.query.filter_by(exchange_id=exchange_id).first()
    user.amount = wallet_value
    db.session.add(user)
    db.session.commit()





    