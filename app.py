import os
import logging

from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask import Flask, jsonify
from flask_migrate import Migrate
from dotenv import load_dotenv


from db import db
import models

from functions import populate_currencies_from_json, update_currency_rates

from resources.currencies import blp as CurrenciesBlueprint
from resources.exchange import blp as ExchangeBlueprint
from resources.history import blp as HistoryBlueprint



def create_app(db_url=None):
    logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
    app = Flask(__name__)
    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "CRYPTO Trader API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    migrate = Migrate(app, db)
    api = Api(app)

    
    @app.before_first_request
    def setup_database():
        logging.info('Setting up database')
        db.create_all()
        json_file_name = "Currency_info.json"
        json_file_path = os.path.join(os.getcwd(), json_file_name)
        if os.path.isfile(json_file_path):
            pass
            populate_currencies_from_json(json_file_path)
            update_currency_rates()
    

    # app.config["JWT_SECRET_KEY"] = "sam"
    
    # jwt = JWTManager(app)

    # @jwt.token_in_blocklist_loader
    # def check_if_token_in_blocklist(jwt_header, jwt_payload):
    #     # Check whether any JWT received is in the blocklist.
    #     jti = jwt_payload["jti"]
    #     return db.session.query(BlocklistModel.query.filter_by(jti=jti).exists()).scalar()

    # @jwt.needs_fresh_token_loader
    # def token_not_fresh_callback(jwt_header, jwt_payload):
    #     return (
    #         jsonify(
    #             {
    #                 "description": "The token is not fresh.", 
    #                 "error": "fresh_token_required",
    #             }
    #         ),
    #         401,
    #     )

    # @jwt.revoked_token_loader
    # def revoked_token_callback(jwt_header, jwt_payload):
    #     return (
    #         jsonify(
    #             {"description": "The token has been revoked.", "error": "token_revoked"}
    #         ),
    #         401,
    #     )

    # @jwt.additional_claims_loader
    # def add_claims_to_jwt(identity):
    #     if identity == 1:
    #         return {"is_admin": True}
    #     return {"is_admin": False}

    # @jwt.expired_token_loader
    # def expired_token_callback(jwt_header, jwt_payload):
    #     return (
    #         jsonify({"message": "The token has expired.", "error": "token_expired"}),
    #         401,
    #     )

    # @jwt.invalid_token_loader
    # def invalid_token_callback(error):
    #     return (
    #         jsonify(
    #             {"message": "Signature verification failed.", "error": "invalid_token"}
    #         ),
    #         401,
    #     )

    # @jwt.unauthorized_loader
    # def missing_token_callback(error):
    #     return (
    #         jsonify(
    #             {
    #                 "description": "Request does not contain an access token.",
    #                 "error": "authorization_required",
    #             }
    #         ),
    #         401,
    #     )
    
    api.register_blueprint(CurrenciesBlueprint)
    api.register_blueprint(ExchangeBlueprint)
    api.register_blueprint(HistoryBlueprint)
    
    return app

# docker build -t trade-api .



# docker run -dp 5000:5000 -w /app -v "/d/Samuel/Python_VSc/Flask_trade_SurgLogs:/app" trade-api