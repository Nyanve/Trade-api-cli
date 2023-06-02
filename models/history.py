from db import db

class HistoryModel(db.Model):
    __tablename__ = 'history'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    currency_in = db.Column(db.String, nullable=False)
    currency_out = db.Column(db.String, nullable=False)
    exchange_id = db.Column(db.Integer, db.ForeignKey('user_log.exchange_id'), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)