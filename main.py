from flask import Flask, render_template, request, redirect, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.String(40), primary_key=True)
    nickname = db.Column(db.String(40))
    salt = db.Column(db.String(100))
    password_hash = db.Column(db.String(40))
    places = db.relationship('Place', backref='user')
    deals = db.relationship('Deal', backref='user')
    times = db.relationship('Time', backref='user')
    duration = db.relationship('Duration', backref='user')


class Place(db.Model):
    place_id = db.Column(db.String(40), primary_key=True)
    place_name = db.Column(db.String(40))
    user_id = db.Column(db.String(40), db.ForeignKey('user.user_id'))
    deals = db.relationship('Deal', backref='place')


class Deal(db.Model):
    deal_id = db.Column(db.String(40), primary_key=True)
    deal_name = db.Column(db.String(40))
    user_id = db.Column(db.String(40), db.ForeignKey('user.user_id'))
    place_id = db.Column(db.String(40), db.ForeignKey('place.place_id'))
    deal_duration = db.relationship('Duration', backref='deal')


class Duration(db.Model):
    duration_id = db.Column(db.String(40), primary_key=True, default=str(uuid.uuid4()))
    user_id = db.Column(db.String(40), db.ForeignKey('user.user_id'))
    place_id_1 = db.Column(db.String(40), db.ForeignKey('place.place_id'))
    place_id_2 = db.Column(db.String(40), db.ForeignKey('place.place_id'))
    route_duration = db.Column(db.Integer)


@app.route('/registration', methods='POST')
def registration():
    user_id = uuid.uuid4()
    nickname = request.form["nickname"]
    salt = request.form["salt"]
    password_hash = request.form["password_hash"]

    user = User(user_id=user_id, nickname=nickname, salt=salt, password_hash=password_hash)

    try:
        db.session.add(user)
        db.session.commit()
        return {"user_id": user_id}
    except:
        return make_response("404 Error", 400)


@app.route('/newplace', methods='POST')
def new_place():
    place_id = uuid.uuid4()
    place_name = request.form["place_name"]
    user_id = request.headers['user_id']

    place = Place(place_id=place_id, place_name=place_name, user_id=user_id)

    try:
        db.session.add(place)
        db.session.commit()
        return {"place_id": place_id}
    except:
        return make_response("404 Error", 400)


@app.route('/newdeal', methods='POST')
def new_deal():
    deal_id = uuid.uuid4()
    deal_name = request.form["deal_name"]
    user_id = request.headers["user_id"]
    place_id = request.headers["place_id"]

    deal = Deal(deal_id=deal_id, deal_name=deal_name, user_id=user_id, place_id=place_id)

    try:
        db.session.add(deal)
        db.session.commit()
        return {"deal_id": deal_id}
    except:
        return make_response("404 Error", 400)


@app.route('/newduration', methods='POST')
def new_duration():
    duration_id = uuid.uuid4()
    user_id = request.form["user_id"]
    place_id_1 = request.form["place_id_1"]
    place_id_2 = request.form["place_id_2"]
    route_duration = 0

    duration = Duration(duration_id=duration_id, user_id=user_id, place_id_1=place_id_1, place_id_2=place_id_2, route_duration=route_duration)

    try:
        db.session.add(duration)
        db.session.commit()
        return {"duration_id": duration_id}
    except:
        return make_response("404 Error", 400)
