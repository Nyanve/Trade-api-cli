from flask.views import MethodView
from flask_smorest import Blueprint, abort
import logging  


from sqlalchemy.exc import SQLAlchemyError


from db import db
from models import UserLogModel
from models import WalletModel
from models import CurrenciesModel
from models import HistoryModel
from schemas import UserLogSchema, WalletSchema, TradeSchema


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
        user_log = UserLogModel(**user_log_data)

        try:
            db.session.add(user_log)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the user log information.")
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

        try:
            update_deposit_amount(cur_shortcut, amount, exchange_id)
        except SQLAlchemyError:
            abort(500, message="An error occurred while updating the deposit in Wallet.")


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
        logging.info(f'The trade is starting {Trade_data}') 
        # Check if the user has enough funds in their wallet, this wil automatically deploy Trade if true
        return check_user_funds(Trade_data, exchange_id)








    

        
    









    # @jwt_required(fresh=True)
    # @blp.arguments(ItemSchema)
    # @blp.response(201, ItemSchema)
    # def post(self, item_data):
    #     item = ItemModel(**item_data)

    #     try:
    #         db.session.add(item)
    #         db.session.commit()
    #     except SQLAlchemyError:
    #         abort(500, message="An error occurred while inserting the item.")

    #     return item

# @blp.route("/item/<int:item_id>")
# class Item(MethodView):
#     @jwt_required()
#     @blp.response(200, ItemSchema)
#     def get(self, item_id):
#         item = ItemModel.query.get_or_404(item_id)
#         return item

#     @jwt_required(fresh=True)
#     def delete(self, item_id):
#         jwt = get_jwt()
#         if not jwt.get("is_admin"):
#             abort(401, message="Admin privilege required.")
#         item = ItemModel.query.get_or_404(item_id)
#         db.session.delete(item)
#         db.session.commit()
#         return {"message": "Item deleted."}

#     @blp.arguments(ItemUpdateSchema)
#     @blp.response(200, ItemSchema)
#     def put(self, item_data, item_id):
#         item = ItemModel.query.get(item_id)
#         if item:
#             item.price = item_data["price"]
#             item.name = item_data["name"]
#         else:
#             item = ItemModel(id=item_id, **item_data)

#         db.session.add(item)
#         db.session.commit()

#         return item


# @blp.route("/item")
# class ItemList(MethodView):
#     @jwt_required()
#     @blp.response(200, ItemSchema(many=True))
#     def get(self):
#         return ItemModel.query.all()

#     @jwt_required(fresh=True)
#     @blp.arguments(ItemSchema)
#     @blp.response(201, ItemSchema)
#     def post(self, item_data):
#         item = ItemModel(**item_data)

#         try:
#             db.session.add(item)
#             db.session.commit()
#         except SQLAlchemyError:
#             abort(500, message="An error occurred while inserting the item.")

#         return item


# @blp.route("/bloklist")
# class Blocklist(MethodView):
#     @blp.response(200, BlocklistSchema(many=True))
#     def get(self):
#         return BlocklistModel.query.all()


    