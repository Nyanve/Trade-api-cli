from db import db

class CurrenciesModel(db.Model):
    __tablename__ = 'currencies'
    
    id = db.Column(db.Integer, primary_key=True)
    cur_name = db.Column(db.String, nullable=False, unique=True)
    cur_shortcut = db.Column(db.String, nullable=False, unique=True)
    symbol = db.Column(db.String)
    cur_to_eur = db.Column(db.Float, nullable=False)
    eur_to_cur = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)



# i need a function that will update "cur_to_eur","eur_to_cur"  to fill this table you will use these links: Get the currency list with EUR as base currency:
# https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/eur.json (this one will give you all currency names 'cur_name' and conversion rate 'eur_to_cur'. 
# Get the currency value for USD to EUR:https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/usd/eur.json (this one will give you conversion rate 'cur_to_eur'ofcourse you need to change the url to get other currencies)
