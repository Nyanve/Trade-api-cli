from db import db

class WalletModel(db.Model):
    __tablename__ = 'wallet'

    id = db.Column(db.Integer, primary_key=True)
    cur_shortcut = db.Column(db.String(3), nullable=False)
    amount = db.Column(db.Float)
    exchange_id = db.Column(db.Integer, db.ForeignKey('user_log.exchange_id'))

    user_log = db.relationship("UserLogModel", back_populates="wallet")
    