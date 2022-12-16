from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
import uuid
import itertools

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
def reg():
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
    nickname = request.json["username"]
    user = User.query.filter(User.nickname == nickname).first()
    if user:
        return {"salt": user.salt}
    else:
        abort(500)


@app.route('/token', methods=["GET"])
def get_token():
    nickname = request.json["username"]
    password_hash = request.json["password_hash"]
    user = User.query.filter(User.nickname == nickname).first()
    if user and password_hash == user.password_hash:
        return {"token": user.user_token}
    else:
        abort(500)


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
            route = Route(route_id=str(uuid.uuid4()),route_duration=0, user_id=user.user_id, place_id_1=place.id, place_id_2=ad_place.id)
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
        place = {"name": place_user.place_name,
                 "place_id": place_user.place_id}
        places.append(place)
    if places:
        return places
    else:
        abort(500)


@app.route('/places/<string:place_id>', methods=["PUT"])
def put_places(place_id):
    place = Place.query.filter(Place.place_id == place_id).first()
    user_token = request.headers["token"]
    true_user = User.query.get(place.user_id)
    if user_token != true_user.user_token:
        abort(500)
    new_name = request.json["name"]
    try:
        place.place_name = new_name
        db.session.commit()
        return {"new_name": new_name}
    except:
        abort(500)


@app.route('/places/<string:place_id>', methods=["DELETE"])
def del_places(place_id):
    place = Place.query.filter(Place.place_id == place_id).first()
    jobs_with_place_id = place.jobs
    for job in jobs_with_place_id:
        db.session.delete(job)
    routes = Route.query.filter(Route.place_id_1 == place.id or Route.place_id_2 == place.id).all()
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
    place_id = request.json["place"]["place_id"]
    place = Place.query.filter(Place.place_id == place_id).first()

    job = Job(job_id=job_id, job_name=job_name, job_duration=job_duration, user_id=user.user_id, place_id=place.id)

    db.session.add(job)
    db.session.commit()
    return {"job_id": job_id}


@app.route('/jobs', methods=["GET"])
def get_job():
    jobs = []
    user_token = request.headers["token"]
    user = User.query.filter(User.user_token == user_token).first()
    places_for_user = user.places
    for place in places_for_user:
        jobs_for_place = place.jobs
        for job_place in jobs_for_place:
            job = {
                "job_id": job_place.job_id,
                "name": job_place.job_name,
                "duration": job_place.job_duration,
                "place": {
                    "name": place.place_name,
                    "place_id": place.place_id
                }
            }
            print(job)
            jobs.append(job)

    print(jobs)
    if jobs:
        return jobs
    else:
        abort(500)


@app.route('/jobs/<string:job_id>', methods=["PUT"])
def put_jobs(job_id):
    job = Job.query.filter(Job.job_id == job_id).first()
    job_name = request.json["name"]
    job_duration = int(request.json["duration"])
    place_id = request.json["place"]["place_id"]
    try:
        job.job_name = job_name
        job.job_duration = job_duration
        job.place_id = place_id
        db.session.commit()
        return {"new_name": job_name}
    except:
        abort(500)


@app.route('/jobs/<string:job_id>', methods=["DELETE"])
def del_job(job_id):
    job = Job.query.filter(Job.job_id == job_id).first()
    name = job.job_name
    try:
        db.session.delete(job)
        db.session.commit()
        return {"deleted": name}
    except:
        abort(500)


@app.route('/routes/<string:route_id>', methods=["PUT"])
def put_route(route_id):
    duration = int(request.json["duration"])
    route = Route.query.filter(Route.route_id == route_id).first()
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
                 "route_id": route_user.route_id,
                 "first_place": {
                     "name": first_place.place_name,
                     "place_id": first_place.place_id
                     },
                 "second_place": {
                     "name": second_place.place_name,
                     "place_id": second_place.place_id
                    }
                 }
        routes.append(route)
    if routes:
        return routes
    else:
        abort(500)


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
    return res_way, min_value


@app.route('/min_way', methods=["GET"])
def get_result():
    start_place_id = request.json["start"]
    place_start = Place.query.filter(Place.place_id == start_place_id).first()
    end_place_id = request.json["end"]
    place_end = Place.query.filter(Place.place_id == end_place_id).first()
    start = place_start.id
    end = place_end.id

    user_token = request.headers["token"]
    user = User.query.filter(User.user_token == user_token).first()
    routes = user.routes
    places_id = []
    for route in routes:
        if route.place_id_1 not in places_id:
            places_id.append(route.place_id_1)
        if route.place_id_2 not in places_id:
            places_id.append(route.place_id_2)
    places_id.sort()
    transition = {}
    number_place = len(places_id)
    graph_start = 0
    graph_end = 0
    for i in range(number_place):
        if places_id[i] == start:
            graph_start = i
        elif places_id[i] == end:
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

    graph_way, value_way = enum(graph_start, graph_end, graph_matrix)
    print(graph_way, value_way)
    way = []
    for i in graph_way:
        place = Place.query.get(transition[i])
        way.append(place.place_id)
    print(way, value_way)
    return {"way": way,
            "time": value_way}


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

