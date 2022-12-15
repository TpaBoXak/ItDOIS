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
    user_token = db.Column(db.String(40))
    nickname = db.Column(db.String(40))
    salt = db.Column(db.String(100))
    password_hash = db.Column(db.String(40))
    # places = db.relationship('Place', backref='user')
    jobs = db.relationship('Job', backref='user')
    # durations = db.relationship('Route', backref='user')


class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.String(40))
    place_name = db.Column(db.String(40))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    jobs = db.relationship('Job', backref='place')
#     route = db.relationship('Place', secondary=Route,  backref='place')


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(40))
    job_name = db.Column(db.String(40))
    job_duration = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))
#
#
# class Route(db.Model):
#     duration_id = db.Column(db.Integer, primary_key=True)
#     route_duration = db.Column(db.Integer)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
#     place_id_1 = db.Column(db.Integer, db.ForeignKey('place.place_id'))
#     place_id_2 = db.Column(db.Integer, db.ForeignKey('place.place_id'))


@app.route('/registration', methods=["POST"])
def reg():
    user_token = str(uuid.uuid4())
    nickname = request.json["nickname"]
    salt = request.json["salt"]
    password_hash = request.json["password_hash"]

    print(user_token, nickname, salt, password_hash)
    user = User(user_token=user_token, nickname=nickname, salt=salt, password_hash=password_hash)

    db.session.add(user)
    db.session.commit()
    return {"user_token": user_token}


@app.route('/user/job', methods=["GET"])
def test():
    user_token = request.headers["user_token"]
    user = User.query.filter(user_token == user_token).first()
    print(user.jobs)
    return {"Lovi aptechku": str(user.jobs)}


@app.route('/places', methods=["POST"])
def new_place():
    place_id = str(uuid.uuid4())
    place_name = request.json["name"]
    user_token = request.headers["user_token"]
    user = User.query.filter(User.user_token == user_token).first()

    print(place_id, place_name, user.user_id)
    place = Place(place_id=place_id, place_name=place_name, user_id=user.user_id)

    try:
        db.session.add(place)
        db.session.commit()
        return {"place_id": place_id}
    except:
        return abort(500)
#
#     adjacent_place = Place.query.filter_by(user_id=user_id).all()
#
#     try:
#         for ad_place in adjacent_place:
#             if place_id == ad_place.place_id:
#                 continue
#             duration_id = int(uuid.uuid4())
#             route = Route(duration_id=duration_id, route_duration=0, user_id=user_id, place_id_1=place_id,
#                           place_id_2=ad_place.place_id)
#             db.session.add(route)
#             db.session.commit()
#         return {"place_id": place_id_str}
#     except:
#         return abort(500)


@app.route('/jobs', methods=["POST"])
def new_deal():
    job_id = str(uuid.uuid4())
    job_name = request.json["name"]
    user_token = request.headers["user_token"]
    user = User.query.filter(User.user_token == user_token).first()
    place_id = request.json["place_id"]
    place = Place.query.filter(Place.place_id == place_id).first()

    job = Job(job_id=job_id, job_name=job_name, job_duration=0, user_id=user.user_id, place_id=place.id)

    db.session.add(job)
    db.session.commit()
    return {"job_id": job_id}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

