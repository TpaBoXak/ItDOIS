from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from random import randint
import uuid
import itertools
from wood_alg import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ItDoLS.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    user_token = db.Column(db.String(40))
    nickname = db.Column(db.String(40))
    salt = db.Column(db.String(100))
    password_hash = db.Column(db.String(40))
    places = db.relationship('Place', backref='user')
    jobs = db.relationship('Job', backref='user')
    routes = db.relationship('Route', backref='user')


class Place(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    place_id = db.Column(db.String(40))
    place_name = db.Column(db.String(40))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    jobs = db.relationship('Job', backref='place')


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.String(40))
    job_name = db.Column(db.String(40))
    job_duration = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    place_id = db.Column(db.Integer, db.ForeignKey('place.id'))


class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    route_id = db.Column(db.String(40))
    route_duration = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    place_id_1 = db.Column(db.Integer)
    place_id_2 = db.Column(db.Integer)


@app.route('/registration', methods=["POST"])
def registration():
    user_token = str(uuid.uuid4())
    nickname = request.json["username"]
    salt = request.json["salt"]
    password_hash = request.json["password_hash"]

    if User.query.filter(User.nickname == nickname).first():
        abort(403)

    user = User(user_token=user_token, nickname=nickname, salt=salt, password_hash=password_hash)

    db.session.add(user)
    db.session.commit()
    return {"token": user_token}


@app.route('/salt', methods=["GET"])
def get_salt():
    nickname = request.headers["username"]
    user = User.query.filter(User.nickname == nickname).first()
    if user:
        return {"salt": user.salt}
    else:
        abort(500)


@app.route('/token', methods=["GET"])
def get_token():
    nickname = request.headers["username"]
    password_hash = request.headers["password_hash"]
    user = User.query.filter(User.nickname == nickname).first()
    if user and password_hash == user.password_hash:
        return {"token": user.user_token}
    else:
        return abort(500)


@app.route('/places', methods=["POST"])
def new_place():
    place_id = str(uuid.uuid4())
    place_name = request.json["name"]
    user_token = request.headers["token"]
    user = User.query.filter(User.user_token == user_token).first()

    place = Place(place_id=place_id, place_name=place_name, user_id=user.user_id)

    try:
        db.session.add(place)
        db.session.commit()
    except:
        return abort(500)

    try:
        adjacent_place = user.places
        for ad_place in adjacent_place:
            if place_id == ad_place.place_id:
                continue
            route = Route(route_id=str(uuid.uuid4()), route_duration=0, user_id=user.user_id, place_id_1=place.id, place_id_2=ad_place.id)
            db.session.add(route)
            db.session.commit()
        return {"place_id": place_id}
    except:
        return abort(500)


@app.route('/places', methods=["GET"])
def get_places():
    places = []
    user_token = request.headers["token"]
    user = User.query.filter(User.user_token == user_token).first()
    places_for_user = user.places
    for place_user in places_for_user:
        place = {"id": place_user.id,
                "name": place_user.place_name,
                "color": place_user.place_id[2:8]}
        places.append(place)
    return places


@app.route('/places/<int:id>', methods=["PUT"])
def put_place(id):
    place = Place.query.get(id)
    user_token = request.headers["token"]
    true_user = User.query.get(place.user_id)
    if user_token != true_user.user_token:
        abort(404)
    new_name = request.json["name"]
    try:
        place.place_name = new_name
        db.session.commit()
        return {"new_name": new_name}
    except:
        abort(500)


@app.route('/places/<int:id>', methods=["DELETE"])
def del_place(id):
    place = Place.query.get(id)
    user_token = request.headers["token"]
    true_user = User.query.get(place.user_id)
    if user_token != true_user.user_token:
        abort(404)
    jobs_with_place_id = place.jobs
    for job in jobs_with_place_id:
        db.session.delete(job)
    routes = Route.query.filter(Route.place_id_1 == id).all()
    for route in routes:
        db.session.delete(route)
    routes = Route.query.filter(Route.place_id_2 == id).all()
    for route in routes:
        db.session.delete(route)
    name = place.place_name
    db.session.delete(place)
    try:
        db.session.commit()
        return {"deleted": name}
    except:
        abort(500)


@app.route('/jobs', methods=["POST"])
def new_job():
    job_id = str(uuid.uuid4())
    job_name = request.json["name"]
    job_duration = int(request.json["duration"])
    user_token = request.headers["token"]
    user = User.query.filter(User.user_token == user_token).first()
    place_id = request.json["place"]["id"]
    place = Place.query.get(int(place_id))

    job = Job(job_id=job_id, job_name=job_name, job_duration=job_duration, user_id=user.user_id, place_id=place.id)

    db.session.add(job)
    db.session.commit()
    return {"job_id": job_id}


@app.route('/jobs', methods=["GET"])
def get_jobs():
    jobs = []
    user_token = request.headers["token"]
    user = User.query.filter(User.user_token == user_token).first()
    places_for_user = user.places
    for place in places_for_user:
        jobs_for_place = place.jobs
        for job_place in jobs_for_place:
            job = {
                "id": job_place.id,
                "name": job_place.job_name,
                "duration": job_place.job_duration,
                "place": {
                    "id": place.id,
                    "name": place.place_name,
                    "color": place.place_id[2:8]
                }
            }
            jobs.append(job)
    return jobs


@app.route('/jobs/<int:id>', methods=["PUT"])
def put_job(id):
    job = Job.query.get(id)
    user_token = request.headers["token"]
    true_user = User.query.get(job.user_id)
    if user_token != true_user.user_token:
        abort(404)
    job_name = request.json["name"]
    job_duration = int(request.json["duration"])
    place_id = request.json["place"]["id"]
    try:
        job.job_name = job_name
        job.job_duration = job_duration
        job.place_id = int(place_id)
        db.session.commit()
        return {"new_name": job_name}
    except:
        abort(500)


@app.route('/jobs/<int:id>', methods=["DELETE"])
def delete_job(id):
    job = Job.query.get(id)
    user_token = request.headers["token"]
    true_user = User.query.get(job.user_id)
    if user_token != true_user.user_token:
        abort(404)
    name = job.job_name
    try:
        db.session.delete(job)
        db.session.commit()
        return {"deleted": name}
    except:
        abort(500)


@app.route('/routes/<int:id>', methods=["PUT"])
def put_route(id):
    duration = int(request.json["duration"])
    route = Route.query.get(id)
    user_token = request.headers["token"]
    true_user = User.query.get(route.user_id)
    if user_token != true_user.user_token:
        abort(404)
    try:
        route.route_duration = duration
        db.session.commit()
        return {"new_duration": duration}
    except:
        abort(500)


@app.route('/routes', methods=["GET"])
def get_routes():
    user_token = request.headers["token"]
    user = User.query.filter(User.user_token == user_token).first()
    routes = []
    routes_for_user = user.routes
    for route_user in routes_for_user:
        first_place = Place.query.filter(Place.id == route_user.place_id_1).first()
        second_place = Place.query.filter(Place.id == route_user.place_id_2).first()
        route = {"duration": route_user.route_duration,
                 "id": route_user.id,
                 "first_place": {
                     "name": first_place.place_name,
                     "color": first_place.place_id[2:8],
                     "id": first_place.id},
                 "second_place": {
                     "color": second_place.place_id[2:8],
                     "name": second_place.place_name,
                     "id": second_place.id}
                 }
        routes.append(route)

    return routes


def enum(start, end, graph):
    res_way = []
    n = len(graph)
    val = [i for i in range(n) if i != start and i != end]
    perm_list = itertools.permutations(val)
    min_value = 24 * 60
    if start == end:
        n += 1
    for i in perm_list:
        temp_list = list(i)
        temp_list.append(end)
        temp_list.insert(0, start)
        temp_value = 0
        for ind in range(1, n):
            temp_value += graph[temp_list[ind-1]][temp_list[ind]]
        if temp_value < min_value:
            min_value = temp_value
            res_way = temp_list
    return res_way


@app.route('/min_way', methods=["GET"])
def get_result():
    start_place_id = request.headers["start"]
    end_place_id = request.headers["end"]

    user_token = request.headers["token"]
    user = User.query.filter(User.user_token == user_token).first()
    places = user.places
    places_id = []
    for place in places:
        if place.jobs or place.id == start_place_id or place.id == end_place_id:
            places_id.append(place.id)
    if not places_id or len(places_id) == 1:
        abort(500)
    places_id.sort()
    transition = {}
    number_place = len(places_id)
    graph_start = 0
    graph_end = 0
    for i in range(number_place):
        if places_id[i] == int(start_place_id):
            graph_start = i
        if places_id[i] == int(end_place_id):
            graph_end = i
        transition[i] = places_id[i]

    graph_matrix = [[0] * number_place for i in range(number_place)]
    for i in range(number_place):
        for j in range(i + 1, number_place):
            route = Route.query.filter(Route.place_id_1 == transition[i], Route.place_id_2 == transition[j]).first()
            if not route:
                route = Route.query.filter(Route.place_id_1 == transition[j], Route.place_id_2 == transition[i]).first()
            graph_matrix[i][j] = route.route_duration
            graph_matrix[j][i] = route.route_duration

    graph_way = way_wood_alg(graph_start, graph_end, graph_matrix)
    way = []
    for i in graph_way:
        place = Place.query.get(transition[i])
        way.append(place.id)

    ways = []
    ways.append(way_to_out(way.copy(), 10))
    ways.append(way_to_out(way.copy(), 8))
    ways.append(way_to_out(way.copy(), 7))
    return {"ways": ways}


def way_to_out(way, rand_temp):
    if rand_temp != 10:
        rand_entry = 0
    else:
        rand_entry = 10
    result_way = {
        "jobs": [],
        "xjobs": [],
        "routes": []
    }

    index_way = 0
    while index_way < len(way):
        jobs = []
        xjobs = []
        place = Place.query.get(way[index_way])
        place_jobs = place.jobs

        index_jobs = 0
        while index_jobs < len(place_jobs):
            if index_way == 0 or index_way == len(way) - 1 or randint(0, 10) < rand_entry:
                jobs.append(place_jobs[index_jobs])
            else:
                rand_entry += rand_temp
                xjobs.append(place_jobs[index_jobs])
            index_jobs += 1

        for xjob in xjobs:
            xjob_to_out = {
                "id": xjob.id,
                "name": xjob.job_name,
                "duration": xjob.job_duration,
                "place": {
                    "id": place.id,
                    "name": place.place_name,
                    "color": place.place_id[2:8]
                }
            }
            result_way["xjobs"].append(xjob_to_out)

        if len(xjobs) == len(place_jobs) and index_way != 0 and index_way != len(way) - 1:
            way.pop(index_way)
        else:
            for job in jobs:
                job_to_out = {
                    "id": job.id,
                    "name": job.job_name,
                    "duration": job.job_duration,
                    "place": {
                        "id": place.id,
                        "name": place.place_name,
                        "color": place.place_id[2:8]
                    }
                }
                result_way["jobs"].append(job_to_out)

        index_way += 1

    for index_way in range(1, len(way)):
        route = Route.query.filter(Route.place_id_1 == way[index_way - 1], Route.place_id_2 == way[index_way]).first()
        first_place = Place.query.get(way[index_way - 1])
        second_place = Place.query.get(way[index_way])

        if not route:
            route = Route.query.filter(Route.place_id_2 == way[index_way - 1], Route.place_id_1 == way[index_way]).first()

        if route:
            route_to_out = {
                "duration": route.route_duration,
                "id": route.id,
                "first_place": {
                    "name": first_place.place_name,
                    "color": first_place.place_id[2:8],
                    "id": first_place.id},
                "second_place": {
                    "color": second_place.place_id[2:8],
                    "name": second_place.place_name,
                    "id": second_place.id}
            }
            result_way["routes"].append(route_to_out)
    return result_way


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
