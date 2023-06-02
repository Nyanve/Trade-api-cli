from flask_smorest import abort
from sqlalchemy.exc import SQLAlchemyError
import json
from datetime import datetime
import requests

from db import db
from models import UserLogModel
from models import WalletModel
from models import CurrenciesModel
from models import HistoryModel
from schemas import UserLogSchema, WalletSchema





def update_deposit_amount(wallet, exchange_id):
    existing_wallet = WalletModel.query.filter_by(cur_shortcut=wallet.cur_shortcut, exchange_id=exchange_id).first()
    if existing_wallet:
        existing_wallet.amount += wallet.amount
    else:
        db.session.add(wallet)

    db.session.commit()


def update_wallet(wallet, exchange_id):
    existing_wallet = WalletModel.query.filter_by(cur_shortcut=wallet.currency_in, exchange_id=exchange_id).first()
    if existing_wallet:
        if existing_wallet.amount >= wallet.amount:
            # Create a new trade and add it to the History and update the Wallet funds
            create_trade(wallet, exchange_id)
            # Subtracts used funds 
            existing_wallet.amount -= wallet.amount

            # Check if the wallet amount dropped to zero, then delets the funds
            if existing_wallet.amount == 0:
                db.session.delete(existing_wallet)
                db.session.commit()

            return True
        else:
            abort(400, message="Not enough funds.")
    else:
        abort(400, message="You dont own enough funds in this currency.")
    

def create_trade(wallet, exchange_id):
    # Implement the logic to create a new trade and return currency_out and amount
    # This is a placeholder and should be replaced with the actual implementation


    # except SQLAlchemyError:
    #                 abort(500, message="An error occurred while creating the trade.")

    
    trade = {
        'currency_out': 'currency_out',
        'amount': 'amount'
    } 
    # Update the Wallet funds
    update_deposit_amount(trade, exchange_id)  
    return trade


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
   
    for currency in CurrenciesModel.query.all():
        cur = currency.cur_shortcut()  # Convert currency code to lowercase
        if cur in eur_data:
            currency.eur_to_cur = eur_data[cur]['eur_to_cur']  

            # Retrieve currency value for currency to EUR
            cur_to_eur_data = requests.get(base_url + f'{cur}/eur.json').json()
            currency.cur_to_eur = cur_to_eur_data['cur_to_eur']

            # Update the timestamp
            currency.timestamp = datetime.now()

    # Commit the changes to the database
    db.session.commit()


# def process_currencies():
#     # Retrieve all rows from the table
#     currencies = CurrenciesModel.query.all()

#     for currency in currencies:
#         cur_shortcut = currency.cur_shortcut
        
#         # Perform actions on the current row
#         # Example actions:
        
#         # 1. Update cur_to_eur and eur_to_cur
#         currency.cur_to_eur = 1.5  # Set a new value for cur_to_eur
#         currency.eur_to_cur = 0.67  # Set a new value for eur_to_cur
        
#         # 2. Update timestamp
#         currency.timestamp = datetime.now()  # Set the current timestamp
        
#         # 3. Add additional actions here as needed
        
#         # Commit the changes to the database
#         db.session.commit()
        
#     return "Currency processing complete."
    

