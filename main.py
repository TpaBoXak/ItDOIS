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
    nickname = request.form['nickname']
    salt = request.form['salt']
    password_hash = request.form['password_hash']
    user_id = uuid.uuid4()

    user = User(user_id=user_id, nickname=nickname, salt=salt, password_hash=password_hash)

    try:
        db.session.add(user)
        db.session.commit()
        return {"user_id": user_id}
    except:
        return make_response("404 Error", 400)


@app.route('/newplace', methods='POST')
def new_place():
