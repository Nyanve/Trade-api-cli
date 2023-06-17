from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import jsonify
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
import json
import os
import threading



from db import db
from models import UserLogModel
from models import WalletModel
from models import CurrenciesModel
from models import HistoryModel
from schemas import CurrenciesSchema, CurrenciesUpdateSchema


from functions import populate_currencies_from_json, update_currencies_background,  update_currency_rates

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
        try:
            json_file_name = "Currency_info.json"
            json_file_path = os.path.join(os.getcwd(), json_file_name)
            if os.path.isfile(json_file_path):
                populate_currencies_from_json(json_file_path)
                return populate_currencies_from_json(json_file_path)
        except:
            abort(409, message="The json file does not exist or is not in the correct format.")


# @blp.route("/currencies/update")
# # Update the currencies table conversion rates with the data from source, conwersion rates are based on EUR and updated every 24 hours 
# class UpdateCurrencies(MethodView):
#     @blp.response(200)
#     def get(self):  
#         return update_currency_rates()
        

            
@blp.route("/currencies/update")
def update_currencies():
    # Start a new thread to execute the update_currencies_background function
    thread = threading.Thread(target=update_currencies_background)
    thread.start()
    update_currencies_background()
    return "Currency update initiated in the background"











        
   