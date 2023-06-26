from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask import jsonify
import logging  


from sqlalchemy.exc import SQLAlchemyError, NoResultFound


from db import db
from models import UserLogModel
from models import WalletModel
from models import CurrenciesModel
from models import HistoryModel
from schemas import UserLogSchema, WalletSchema, TradeSchema, HistorySchema


from functions import update_deposit_amount, check_user_funds



blp = Blueprint("Exchange", "exhange", description="Operations on exchanges.")


@blp.route("/exchanges")
class UserLog(MethodView):
    # This route will return all Users in the database with their wallet funds
    @blp.response(200, UserLogSchema(many=True))
    def get(self):
        return UserLogModel.query.all()
    
    # This route will create a new user log 
    @blp.arguments(UserLogSchema)
    @blp.response(201, UserLogSchema)
    def post(self, user_log_data):
        # get the currency shortcut from the user_log_data
        cur_shortcut = user_log_data['currency']
        
        # add amount to user_log_data and give it walue0.0 and put it in the user_log
        user_log_data['amount'] = 0.0
        user_log = UserLogModel(**user_log_data)
        
        # make amount 0.0 and put it in the user_log
        try:
            currency = CurrenciesModel.query.filter_by(cur_shortcut=cur_shortcut).first()
            if currency is None:
                raise NoResultFound
        except NoResultFound:
            abort(409, message="Currency that you chose is not in the database or does not exist.")

        try:
            db.session.add(user_log)
            db.session.commit()
                
        except SQLAlchemyError:
            abort(409, message="A user with that username already exists.")
        
        logging.info(f'The exchange is created {user_log}')
        return user_log, 201
  

@blp.route("/exchanges/<int:exchange_id>")
class Wallet(MethodView):
    # This route will return all the wallet funds for a specific user
    @blp.response(200, WalletSchema(many=True))
    def get(self, exchange_id):
        return WalletModel.query.filter_by(exchange_id=exchange_id).all()
    
    # This route will deposit funds into the wallet of a specific user
    @blp.arguments(WalletSchema)
    @blp.response(201, WalletSchema)
    def post(self, Wallet_data, exchange_id):
        wallet = WalletModel(**Wallet_data)
        # get the walues out of the wallet
        cur_shortcut = Wallet_data.get('cur_shortcut')
        amount = Wallet_data.get('amount')
        # check if the amount is positive
        if amount <= 0:
            abort(400, message="The amount must be positive.")

        try:
            currency = CurrenciesModel.query.filter_by(cur_shortcut=cur_shortcut).first()
            if currency is None:
                raise NoResultFound
        except NoResultFound:
            abort(409, message="Currency that you chose is not in the database or does not exist.")

        try:
            update_deposit_amount(cur_shortcut, amount, exchange_id)
            logging.info(f'The deposit is created {wallet}')
        except SQLAlchemyError:
            abort(500, message="An error occurred while updating the deposit in Wallet.")

    # This route will delete user log with a specific id
    def delete(self, exchange_id):
        user_log = UserLogModel.query.get_or_404(exchange_id)
        db.session.delete(user_log)
        db.session.commit()
        return {"message": "User log deleted succesfuly."}



@blp.route("/exchanges/del/<int:id>")
class WalletDelete(MethodView):
    # This route will delete wallet fund with a specific id
    def delete(self, id):
        wallet = WalletModel.query.get_or_404(id)
        db.session.delete(wallet)
        db.session.commit()
        return {"message": "Funds deleted succesfuly."}
            
        
@blp.route("/exchanges/<int:exchange_id>/trades")
class UserTrade(MethodView):
    # This route will make a trade for a specific user
    @blp.arguments(TradeSchema)
    @blp.response(201, TradeSchema)
    def post(self, Trade_data, exchange_id):
        # Check if the user has enough funds in their wallet, this wil automatically deploy Trade if true
        trade_data = check_user_funds(Trade_data, exchange_id)
        
        return jsonify(trade_data), 201




