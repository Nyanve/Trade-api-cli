from flask_smorest import abort
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from datetime import datetime
import requests
import logging


from db import db
from models import UserLogModel
from models import WalletModel
from models import CurrenciesModel
from models import HistoryModel
from models import LikedModel
from schemas import UserLogSchema, WalletSchema

thread_local_session = scoped_session(sessionmaker())

def update_deposit_amount(cur_shortcut, amount, exchange_id):
    # Check if the user already has funds in this currency
    existing_wallet = WalletModel.query.filter_by(cur_shortcut=cur_shortcut, exchange_id=exchange_id).first()
    if existing_wallet:
        existing_wallet.amount += amount
    # If not, create a new fund 
    else:
        wallet = WalletModel(cur_shortcut=cur_shortcut, amount=amount, exchange_id=exchange_id)
        db.session.add(wallet)
    calculate_wallet_value(exchange_id)
    db.session.commit()


def check_user_funds(wallet, exchange_id):
    currency_in = wallet.get('currency_in')
    amount = wallet.get('amount')
    existing_wallet = WalletModel.query.filter_by(cur_shortcut=currency_in, exchange_id=exchange_id).first()
    if existing_wallet:
        if existing_wallet.amount >= amount:
            # Create a new trade and add it to the History and update the Wallet funds
            trade_data = make_trade(wallet, exchange_id)
            # Subtracts used funds 
            existing_wallet.amount -= amount
            db.session.commit()

            # Check if the wallet amount dropped to zero, then delets the funds
            if existing_wallet.amount == 0:
                db.session.delete(existing_wallet)
                db.session.commit()
            calculate_wallet_value(exchange_id)

        else:
            abort(400, message="Not enough funds.")
    else:
        abort(400, message="You dont own funds in this currency.")
    return trade_data
    

def make_trade(wallet, exchange_id):
    # get the walues out of the wallet it is a dict
    currency_in = wallet.get('currency_in')
    currency_out = wallet.get('currency_out')
    amount = wallet.get('amount')

    # check if the amount is positive
    if amount <= 0:
        abort(400, message="The amount must be positive.")
    
    # Get the exchange rate from currency_in to EUR
    cur_to_eur = CurrenciesModel.query.filter_by(cur_shortcut=currency_in).first().cur_to_eur
    # Calculate the amount in EUR
    amount_eur = amount * cur_to_eur

    # Get the exchange rate from EUR to currency_out
    eur_to_cur = CurrenciesModel.query.filter_by(cur_shortcut=currency_out).first().eur_to_cur
    # Calculate the amount in currency_out
    amount_out = amount_eur * eur_to_cur


    # Add the trade to the History
    history = HistoryModel(amount=amount, currency_in=currency_in, currency_out=currency_out, exchange_id=exchange_id, timestamp=datetime.now() )
    db.session.add(history)
    db.session.commit()
    
    # Update the Wallet funds
    update_deposit_amount(currency_out, amount_out, exchange_id)
    # change the amount_out to string
    
    logging.info(f'Trade has been made: {amount} {currency_in} -> {amount_out} {currency_out}')
    trade_data = {'amount_out': amount_out, 'currency_out': currency_out}
    return trade_data


def populate_currencies_from_json(json_file_path):
    # check if the database is empty
    if CurrenciesModel.query.first():
        return  
    
    # Load data from JSON file
    with open(json_file_path, encoding='utf-8') as file:
        data = json.load(file)

    # Go through all the currencies in the JSON file and add them to the list 
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
    # Add the currencies to the database
    for currency in currencies:
        currency['cur_shortcut'] = CurrenciesModel(
            cur_name=currency['cur_name'],
            cur_shortcut=currency['cur_shortcut'],
            symbol=currency['symbol'],
            cur_to_eur=0.0,  # Set appropriate values
            eur_to_cur=0.0,  # Set appropriate values
            timestamp=datetime.now()   # Set appropriate values
        )
        db.session.add(currency['cur_shortcut'])

    db.session.commit()


def update_currencies_background():
    # Performing the time-consuming func
    update_currency_rates()


def update_currency_rates():
    try:
        base_url = 'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/'
        eur_data = requests.get(base_url + 'eur.json').json()
        
        for currency in CurrenciesModel.query.all():
            update_currency(currency, eur_data, base_url)

        db.session.commit()

        for user in UserLogModel.query.all():
            calculate_wallet_value(user.exchange_id)
        logging.info('Currency rates updated and wallet walue calculated.')
        return {'message': 'Currency rates updated successfully.'}, 200
    except:
        abort(409, message="An error occurred during currency update processvvyviub.")


def update_currency(currency, eur_data, base_url):

    cur = currency.cur_shortcut.lower()
    if currency.timestamp.date() == datetime.now().date() and currency.eur_to_cur != 0.0:
        return

    if cur in eur_data['eur']:
        currency.eur_to_cur = eur_data["eur"][cur]

        cur_to_eur_data = requests.get(base_url + f'{cur}/eur.json').json()
        currency.cur_to_eur = cur_to_eur_data["eur"]
 
        currency.timestamp = datetime.now()

        db.session.add(currency)
        return {'message': f'Currency updated successfully.'}, 200
        
    
def calculate_wallet_value(exchange_id):
    # go trought all the funds in wallet and calculate the value of the wallet in EUR 
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


def add_to_liked(cur_shortcut, exchange_id):
    logging.info(f'Adding {cur_shortcut} to liked currencies for user with exchange_id {exchange_id}.')
    # check if the currency is already in the liked currencies
    if LikedModel.query.filter_by(cur_shortcut=cur_shortcut, exchange_id=exchange_id).first():
        abort(409, message="This currency is already in your liked currencies.")

    # add the currency to the liked currencies
    liked_currency = LikedModel(cur_shortcut=cur_shortcut, exchange_id=exchange_id)
    db.session.add(liked_currency)
    db.session.commit()

    return {'message': 'Currency added to liked currencies successfully.'}, 200


def remove_from_liked(cur_shortcut, exchange_id):
    logging.info(f'Removing {cur_shortcut} from liked currencies for user with exchange_id {exchange_id}.')
    # check if the currency is already in the liked currencies
    liked_currency = LikedModel.query.filter_by(cur_shortcut=cur_shortcut, exchange_id=exchange_id).first()
    if not liked_currency:
        abort(409, message="This currency is not in your liked currencies.")

    # remove the currency from the liked currencies
    db.session.delete(liked_currency)
    db.session.commit()

    return {'message': 'Currency removed from liked currencies successfully.'}, 200
