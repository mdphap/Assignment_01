from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/auction'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Items(db.Model):
    item_id = db.Column(db.Integer, primary_key = True)
    item_name = db.Column(db.String(50), nullable=False)
    item_desc = db.Column(db.String(225), nullable=False)
    start_time = db.Column(db.DateTime)
    end_time = db.Column(db.DateTime)
    bids = db.relationship('Bids', backref='item',lazy='dynamic')

    def __init__(self, item_name, item_desc):
        self.item_name = item_name
        self.item_desc = item_desc
    
class Users(db.Model):
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable=False)
    biddens = db.relationship('Bids',backref='user',lazy='dynamic')

    def __init__(self, username, password):
        self.username = username
        self.password = password
        
    def auction(self, item_id):
        auctioned_item = Items.query.filter_by(item_id = item_id).first()
        if auctioned_item is None:
            print('This item is not existed.')
        elif auctioned_item.start_time is None:
            auctioned_item.start_time = datetime.isoformat(datetime.now())
            db.session.commit()
            print('This item is on auction now!')
        else:
            print('This item had been auctioned!')
            
    def bid(self, item_id, bid_price):
        auctioned_item = Items.query.filter_by(item_id = item_id).first()
        if auctioned_item is None:
            print('This item is not existed.')
        else:
            if auctioned_item.start_time is not None:
                if auctioned_item.end_time is not None:
                    print('The auction had finished!')
                else:
                    new_bid = Bids(user_id = self.user_id, item_id = item_id, bid_price = bid_price)
                    db.session.add(new_bid)
                    db.session.commit()
            else:
                print('Please auction this item first!')

class Bids(db.Model):
    bid_id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.item_id'))
    bid_price = db.Column(db.Float, nullable=False)

def close_auction(item_id):
    bids_list = Bids.query.filter_by(item_id = item_id).all()
    if len(bids_list) == 0:
        print('This item is not auction yet or there is no bid!')
    else:
        win_price = 0
        win_user_id = 0
        for bid in bids_list:
            if bid.item.end_time is None and bid.bid_price > win_price:
                win_price = bid.bid_price
                win_user_id = bid.user_id
        if (win_price != 0) & (win_user_id != 0):
            winner = Users.query.filter_by(user_id = win_user_id).first().username
            item = Items.query.filter_by(item_id = item_id).first()
            item_name = item.item_name
            item_desc = item.item_desc
            item.end_time = datetime.isoformat(datetime.now())
            db.session.commit()
            print('==RESULT==\nItem: {}\nItem Descriptions: {}\nWinner: {}\nPrice: {}\n==END=='.format(item_name,item_desc,winner,win_price))
        else:
            print('This item\'s auction is finished!')
