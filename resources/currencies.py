from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import json



from db import db
from models import UserLogModel
from models import WalletModel
from models import CurrenciesModel
from models import HistoryModel
from schemas import CurrenciesSchema, CurrenciesUpdateSchema


from functions import populate_currencies_from_json, update_currency_rates

blp = Blueprint("Currencies", "currencies", description="Operations on currencies.")


@blp.route("/currencies")
# This route will return all the currencies in the database
class Currencies(MethodView):
    @blp.response(200, CurrenciesSchema(many=True))
    def get(self):
        return CurrenciesModel.query.all()
          

@blp.route("/currencies/populate")
# Polulate the currencies table with the data from the json file run this route only once when building the database
class PopulateCurrencies(MethodView):
    @blp.response(200, CurrenciesSchema(many=True))
    def get(self):
        json_file_path = 'D:\Samuel\Python_VSc\Flask_trade_SurgLogs\Currency_info.json'
        return populate_currencies_from_json(json_file_path)


@blp.route("/currencies/update")
# Update the currencies table conversion rates with the data from source, conwersion rates are based on EUR and updated every 24 hours 
class UpdateCurrencies(MethodView):
    @blp.response(200)
    def get(self):  
        return update_currency_rates()
        

            












        
   