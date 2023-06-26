from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import jsonify
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from flask import request
import json
import os
import threading
import logging
import requests



from db import db
from models import UserLogModel
from models import WalletModel
from models import CurrenciesModel
from models import HistoryModel
from models import LikedModel
from schemas import CurrenciesSchema, CurrenciesUpdateSchema, LikedSchema


from functions import populate_currencies_from_json, update_currencies_background,  update_currency, add_to_liked, remove_from_liked

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
        
    
@blp.route("/currencies/update")
class UpdateCurrencies(MethodView):
    def get(self):
        # Start a new thread to execute the update_currencies_background function
        thread = threading.Thread(target=update_currencies_background)
        thread.start()
        update_currencies_background()
        return "Currency update initiated in the background"


@blp.route("/update_currency", methods=['POST'])
class UpdateCurrency(MethodView):
    # This route will update specific currency in the database
    def post(self):

            base_url = 'https://cdn.jsdelivr.net/gh/fawazahmed0/currency-api@1/latest/currencies/'
            eur_data = requests.get(base_url + 'eur.json').json()

            cur_shortcut = request.json.get('cur_shortcut')  # Retrieve the currency shortcut from the request payload
            logging.info(f'Updating currency {cur_shortcut} through bulk action.')
            currency = CurrenciesModel.query.filter_by(cur_shortcut=cur_shortcut).first()
            if not currency:
                return jsonify({'message': 'Currency not found'}), 404

            
            return jsonify(update_currency(currency, eur_data, base_url))



@blp.route("/add_to_liked", methods=['POST'])
class AddToLiked(MethodView):
    # This route will add the currency to the liked list
    def post(self):
        cur_shortcut = request.json.get('cur_shortcut')
        exchange_id = request.json.get('exchange_id')

        currency = CurrenciesModel.query.filter_by(cur_shortcut=cur_shortcut).first()
        if not currency:
            abort(404, message="Currency not found in the database")
        
        return jsonify(add_to_liked(cur_shortcut, exchange_id))
        


@blp.route("/remove_from_liked", methods=['POST'])
class RemoveFromLiked(MethodView):
    # This route will remove the currency from the liked list
    def post(self):
        cur_shortcut = request.json.get('cur_shortcut')
        exchange_id = request.json.get('exchange_id')

        currency = CurrenciesModel.query.filter_by(cur_shortcut=cur_shortcut).first()
        if not currency:
            abort(404, message="Currency not found in the database")
        
        return jsonify(remove_from_liked(cur_shortcut, exchange_id))

@blp.route("/liked")
# This route will return all the currencies in the liked database
class Liked(MethodView):
    @blp.response(200, LikedSchema(many=True))
    def get(self):
        return LikedModel.query.all()
    










        
   