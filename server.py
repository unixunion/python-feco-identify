import json
import logging
import sqlite3
from functools import wraps

import numpy as np
from flask import Flask, request, send_from_directory, g, redirect, session
from flask import Response
from flask import url_for

from ai import Matrix

DATABASE = 'database.db'

# initialize the Matrix with label=3 ( category ) and max_features=3 inclusive of depth data
# ai = Matrix(l=3, max_features=3)
# ai2 = Matrix(l=3, max_features=2)

ai_sessions = {}

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')
app.config['DEBUG'] = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


def notnull(name, obj):
    print("Checking %s object %s is not None or ''" % (name, obj))
    if obj is not None and obj is not '' and obj is not u"" and obj is not u'':
        return
    else:
        print("%s is not set" % name)
        raise Exception("%s is empty" % name)



"""
New Auth Stuff
"""
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("login")
    if request.method == 'POST':
        data = request.get_json(force=True)
        if check_auth(data['username'], data['password']):
            print("Login Success")
            session['username'] = data['username']
            ai_sessions["%s-ai" % session['username']] = Matrix(l=3, max_features=3)
            ai_sessions["%s-ai2" % session['username']] = Matrix(l=3, max_features=2)
            retrain_session()
            # print("Redirecting to %s" % url_for("root"))
            return '{"result": "ok"}'
        else:
            return '{"result": "error"}'
    else:
        return send_from_directory('static', 'login.html')

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    session.pop('username', None)
    return redirect("/login")


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'keghol' and password == 'co1n'


# def authenticate():
#     """Sends a 401 response that enables basic auth"""
#     return Response(
#         'Could not verify your access level for that URL.\n'
#         'You have to login with proper credentials', 401,
#         {'WWW-Authenticate': 'Basic realm="Login Required"'})


# def requires_auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth = request.authorization
#         if not auth or not check_auth(auth.username, auth.password):
#             return authenticate()
#         return f(*args, **kwargs)
#
#     return decorated


@app.before_first_request
def setup_logging():
    if not app.debug:
        # In production mode, add log handler to sys.stderr.
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)
    else:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/static/<path:path>')
def send_js(path):
    return send_from_directory('static', path)


# guess a find
# @app.route("/guess/<int:fe>/<int:co>")
# def guess(fe, co):
#     print("Guessing")
#     for g in query_db('select * from feco'):
#         print g
#     return send_from_directory('static', 'index.html')


# log a new find
# @app.route("/log/<int:fe>/<int:co>/<id>", methods=['GET', 'POST'])
# def log(fe, co, id):
#     print("Logging")
#     # query_db('insert into feco (fe, co, id) VALUES (%s, %s, "%s")' % (fe , co, id))
#     insert(fe, co, id)
#     return send_from_directory('static', 'index.html')


@app.route("/ids")
# @requires_auth
def ids():
    l = {}
    try:
        for k in ai_sessions["%s-ai" % session['username']].mydata.target_names:
            l[k] = None
        return json.dumps(l)
    except Exception, e:
        return redirect("/login")


@app.route("/fields")
def fields():
    print("Getting fields")
    fl = {}
    try:
        list_fields = query_db('Select DISTINCT fieldid from feco WHERE userid IS "%s"' % session['username'])
        print("List of fields: %s" % list_fields)
        for f in list_fields:
            fl[f[0]] = None
        return json.dumps(fl)
    except Exception, e:
        print(e.message)
        return redirect("/login")

@app.route("/categories")
# @requires_auth
def categories():
    l = {}
    try:
        for k in ai_sessions["%s-ai" % session['username']].mydata.target_data:
            l[k] = None
        return json.dumps(l)
    except Exception, e:
        return redirect("/login")


@app.route("/", methods=['GET', 'POST'])
def root():
    print("Root")
    if 'username' in session:
        print("User %s is logged in" % session['username'])
        try:
            notnull("ai", ai_sessions["%s-ai" % session['username']])
            notnull("ai2", ai_sessions["%s-ai2" % session['username']])
        except Exception, e:
            return redirect("/login")

        if request.method == 'POST':
            # print("post")
            data = request.get_json(force=True)
            print(data)

            if (data['button'] == 'record'):
                try:
                    notnull("fe", data['fe'])
                    notnull("co", data['co'])
                    notnull("depth", data['depth'])
                    notnull("name", data['id'])
                    notnull("category", data['category'])
                    notnull("field", data['field'])
                    print("Recording findings: %s" % data)
                    try:
                        insert(data['fe'], data['co'], data['depth'], data['id'], data['category'], session['username'], data['field'])
                    except Exception, e:
                        return '{"result": "error: %s}' % e
                    retrain_session()
                    return '{"result": "accepted and retrained"}'
                except Exception, e:
                    return '{"result": "error, %s" }' % e.message
            elif (data['button'] == 'guess'):

                results = []
                appr = {}

                try:
                    print("Guessing: %s" % data)
                    notnull("fe", data['fe'])
                    notnull("co", data['co'])

                    if data['depth']:
                        for name, clf in ai_sessions["%s-ai" % session['username']].compiled_classifiers:
                            print("Depth set, so 3 feature testing")
                            appr = {"classifier": name,
                                    "result": ai_sessions["%s-ai" % session['username']].mydata.target_data[
                                        clf.predict(np.array([data['fe'], data['co'], data['depth']]).reshape(1, -1))[0]]
                                    }
                            results.append(json.dumps(appr))
                    else:
                        for name, clf in ai_sessions["%s-ai2" % session['username']].compiled_classifiers:
                            print("2 feature testing")
                            appr = {"classifier": name,
                                    "result": ai_sessions["%s-ai2" % session['username']].mydata.target_data[
                                        clf.predict(np.array([data['fe'], data['co']]).reshape(1, -1))[0]]
                                    }
                            results.append(json.dumps(appr))
                    print(results)
                    return '{"result": %s }' % json.dumps(results)
                except Exception, e:
                    print("fe/co not set")
                    results.append(json.dumps({"result": "%s" % e.message}))
                    return '{"result": %s }' % json.dumps(results)
            elif data['button'] == 'retrain':
                try:
                    retrain_session()
                    return '{"result": "retrained" }'
                except Exception, e:
                    return '{"result": "error retraining" }'


        else:
            return send_from_directory('static', 'index.html')
    else:
        print("Unknown user")
        return redirect("/login")


def insert(fe, co, depth, id, category, userid, field):
    with app.app_context():
        # g.db is the database connection
        query = 'INSERT INTO feco (fe, co, depth, id, category, userid, fieldid) VALUES (%s, %s, %s,"%s", "%s", "%s", "%s")' % (
            fe, co, depth, id, category, userid, field)
        cur = get_db().execute(query)
        # cur.execute(query, values)
        get_db().commit()
        # id = cur.lastrowid
        cur.close()
        return id


def query_db(query, args=(), one=False):
    with app.app_context():
        cur = get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv


def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()
        # insert(99, 99, 99,"test id", "test category")
        # insert(90, 90, 90, "test id", "test category")
        # insert(80, 80, 99, "test id", "test category")


def retrain_session():
    with app.app_context():
        dbdata = query_db("SELECT fe, co, depth, id, category from feco WHERE userid IS '%s'" % session['username'])
        print("Dumping DB")
        print(dbdata)
        for rec in dbdata:
            print(list(rec))
            ai_sessions["%s-ai" % session['username']].mydata.da.append(list(rec))
            ai_sessions["%s-ai2" % session['username']].mydata.da.append(list(rec))
        print("Ai data:")
        print(ai_sessions["%s-ai" % session['username']].mydata.da)

        ai_sessions["%s-ai" % session['username']].mydata.rebuild(l=4)
        ai_sessions["%s-ai" % session['username']].rebuild()

        ai_sessions["%s-ai2" % session['username']].mydata.rebuild(l=4)
        ai_sessions["%s-ai2" % session['username']].rebuild()



# def retrain():
#     # os.system("say 'Matrix retraining'")
#     dbdata = query_db("SELECT fe, co, depth, id, category from feco")
#     print("Dumping DB")
#     print(dbdata)
#     for rec in dbdata:
#         print(list(rec))
#         ai.mydata.da.append(list(rec))
#         ai2.mydata.da.append(list(rec))
#     print("Ai data:")
#     print(ai.mydata.da)
#
#     ai.mydata.rebuild(l=4)
#     ai.rebuild()
#
#     ai2.mydata.rebuild(l=4)
#     ai2.rebuild()


if __name__ == "__main__":
    try:
        init_db()
    except Exception, e:
        print("DB Already initialized")
    # retrain()
    app.run(host='0.0.0.0', port=5000, debug=True)
