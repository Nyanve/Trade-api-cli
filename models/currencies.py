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



