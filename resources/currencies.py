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
from schemas import CurrenciesSchema


from functions import populate_currencies_from_json, update_currency_rates

blp = Blueprint("Currencies", "currencies", description="Operations on currencies.")


@blp.route("/currencies")
# This route will return all the currencies in the database
class Currencies(MethodView):
    @blp.response(200, CurrenciesSchema(many=True))
    def get(self):
        return CurrenciesModel.query.all()
    


# This route will return currency in the database by id
# 
# -_____________________________________________________________________________________________________________________________________________
# TUTO JE TEN PROBEM INT FUNGUJE ALE STRING NIE  potom function.py update_currency_rates() kukni
#---------------------------------------------------------------------------------------------------------------------------------------------- 
# 
@blp.route("/currencies/<int:cur_shortcut>")
class Currencies(MethodView):    
    @blp.response(200, CurrenciesSchema)
    def get(self, cur_shortcut):
        currency = CurrenciesModel.query.get_or_404(cur_shortcut)
        return currency

            
        
 
# Polulate the currencies table with the data from the json file run this route only once when building the database 
@blp.route("/currencies/populate")
class PopulateCurrencies(MethodView):
    @blp.response(200, CurrenciesSchema(many=True))
    def get(self):
        json_file_path = 'D:\Samuel\Python_VSc\Flask_trade_SurgLogs\Currency_info.json'
        return populate_currencies_from_json(json_file_path)


# Update the currencies table conversion rates with the data from source, conwersion rates are based on EUR and updated every 24 hours 
@blp.route("/currencies/update")
class UpdateCurrencies(MethodView):
    @blp.response(200, CurrenciesSchema(many=True))
    def get(self):
        update_currency_rates()
        return CurrenciesModel.query.all()




        
   