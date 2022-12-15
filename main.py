from flask import Flask, request, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
import uuid
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_id_str = db.Column(db.String(40))
    nickname = db.Column(db.String(40))
    salt = db.Column(db.String(100))
    password_hash = db.Column(db.String(40))
    places = db.relationship('Place', backref='user')
    jobs = db.relationship('Job', backref='user')
    durations = db.relationship('Route', backref='user')


class Place(db.Model):
    place_id = db.Column(db.Integer, primary_key=True)
    place_id_str = db.Column(db.String(40))
    place_name = db.Column(db.String(40))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    jobs = db.relationship('Job', backref='place')
    route = db.relationship('Route', backref='place')


class Job(db.Model):
    job_id = db.Column(db.Integer, primary_key=True)
    job_id_str = db.Column(db.String(40))
    job_name = db.Column(db.String(40))
    job_duration = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    place_id = db.Column(db.Integer, db.ForeignKey('place.place_id'))


class Route(db.Model):
    duration_id = db.Column(db.Integer, primary_key=True)
    route_duration = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    place_id_1 = db.Column(db.Integer, db.ForeignKey('place.place_id'))
    place_id_2 = db.Column(db.Integer, db.ForeignKey('place.place_id'))


@app.route('/registration', methods=["POST"])
def reg():
    rand_id = uuid.uuid4()
    user_id = int(rand_id)
    user_id_str = str(rand_id)
    nickname = request.json["nickname"]
    salt = request.json["salt"]
    password_hash = request.json["password_hash"]

    user = User(user_id=user_id, user_id_str=user_id_str, nickname=nickname, salt=salt, password_hash=password_hash)

    try:
        db.session.add(user)
        db.session.commit()
        return {"user_id": user_id_str}
    except:
        return abort(500)


@app.route('/places', methods=["POST"])
def new_place():
    rand_id = uuid.uuid4()
    place_id = int(rand_id)
    place_id_str = str(rand_id)
    place_name = request.json["place_name"]
    user_id = int(request.headers["user_id"])

    place = Place(place_id=place_id, place_id_str=place_id_str, place_name=place_name, user_id=user_id)

    try:
        db.session.add(place)
        db.session.commit()
    except:
        return abort(500)

    user = User.query.get(user_id)
    adjacent_place = user.places.all()

    try:
        for ad_place in adjacent_place:
            duration_id = int(uuid.uuid4())
            route = Route(duration_id=duration_id, route_duration=0, user_id=user.user_id, place_id_1=place_id,
                          place_id_2=ad_place.place_id)
            db.session.add(route)
            db.session.commit()
        return {"place_id": place_id_str}
    except:
        return abort(500)


@app.route('/jobs', methods=["POST"])
def new_deal():
    rand_id = uuid.uuid4()
    job_id = int(rand_id)
    job_id_str = str(rand_id)
    job_name = request.json["job_name"]
    user_id = int(request.headers["user_id"])
    place_id = int(request.headers["place_id"])

    deal = Job(job_id=job_id, job_id_str=job_id_str, job_name=job_name, user_id=user_id, place_id=place_id)

    try:
        db.session.add(deal)
        db.session.commit()
        return {"deal_id": job_id_str}
    except:
        return abort(500)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
