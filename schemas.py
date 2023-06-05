from marshmallow import Schema, fields


class PlainUserLogSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    currency = fields.Str(required=True)
    amount = fields.Float(required=True)

class PlainWalletSchema(Schema):
    id = fields.Int(dump_only=True)
    cur_shortcut = fields.Str(required=True)
    amount = fields.Float(required=True)
    

class HistorySchema(Schema):
    id = fields.Int(dump_only=True)
    amount = fields.Float(required=True)
    currency_in = fields.Str(required=True)
    currency_out = fields.Str(required=True)
    exchange_id = fields.Int(required=True, load_only=True)
    timestamp = fields.DateTime(required=True)

class CurrenciesSchema(Schema):
    id = fields.Int(dump_only=True)
    cur_name = fields.Str(required=True)
    cur_shortcut = fields.Str(required=True)
    symbol = fields.Str()
    cur_to_eur = fields.Float(required=True)
    eur_to_cur = fields.Float(required=True)
    timestamp = fields.DateTime(required=True)

class CurrenciesUpdateSchema(Schema):
    cur_shortcut = fields.Str(required=True)

class TradeSchema(Schema): 
    amount = fields.Float(required=True)
    currency_in = fields.Str(required=True)
    currency_out = fields.Str(required=True)
    

class WalletSchema(PlainWalletSchema):
    exchange_id = fields.Int(load_only=True)
    user_log = fields.Nested(PlainUserLogSchema(), dump_only=True)


class UserLogSchema(PlainUserLogSchema):
    wallet = fields.List(fields.Nested(PlainWalletSchema()), dump_only=True)
 



    


