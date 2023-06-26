from db import db

class UserLogModel(db.Model):
    __tablename__ = 'user_log'

    exchange_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)	
    currency = db.Column(db.String(3), nullable=False) 
    amount = db.Column(db.Float, nullable=False)

    wallet = db.relationship("WalletModel", back_populates="user_log", lazy="dynamic", cascade="save-update, merge, delete")
    liked = db.relationship("LikedModel", back_populates="user_log", lazy="dynamic", cascade="save-update, merge, delete")
    