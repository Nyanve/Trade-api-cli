from db import db

class LikedModel(db.Model):
    __tablename__ = 'Liked'
    id = db.Column(db.Integer, primary_key=True)
    cur_shortcut = db.Column(db.String(3), nullable=False)
    exchange_id = db.Column(db.Integer, db.ForeignKey('user_log.exchange_id'))

    user_log = db.relationship("UserLogModel", back_populates="liked")