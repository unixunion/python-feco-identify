import logging
import sqlite3
from flask import Flask, request, send_from_directory, g
from ai import Matrix
import numpy as np
import json
import os

DATABASE = 'database.db'

# initialize the Matrix with label=3 ( category ) and max_features=3 inclusive of depth data
ai = Matrix(l=3, max_features=3)

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')
app.config['DEBUG'] = True


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
@app.route("/guess/<int:fe>/<int:co>")
def guess(fe, co):
    print("Guessing")
    for g in query_db('select * from feco'):
        print g
    return send_from_directory('static', 'index.html')


# log a new find
@app.route("/log/<int:fe>/<int:co>/<id>", methods=['GET', 'POST'])
def log(fe, co, id):
    print("Logging")
    # query_db('insert into feco (fe, co, id) VALUES (%s, %s, "%s")' % (fe , co, id))
    insert(fe, co, id)
    return send_from_directory('static', 'index.html')


@app.route("/ids")
def ids():
    l = {}
    for k in ai.mydata.target_names:
        l[k] = None
    return json.dumps(l)


@app.route("/categories")
def categories():
    l = {}
    for k in ai.mydata.target_data:
        l[k] = None
    return json.dumps(l)


@app.route("/", methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        print("post")
        data = request.get_json(force=True)
        print(data['fe'])

        if (data['button'] == 'record'):
            print("Recording findings: %s" % data)
            try:
                insert(data['fe'], data['co'], data['depth'], data['id'], data['category'])
            except Exception, e:
                return '{"result": "error: %s}' % e
            return '{"result": "ok"}'
        elif (data['button'] == 'guess'):
            print("Guessing: %s" % data)
            results = []
            for name, clf in ai.compiled_classifiers:
                appr = {}
                if data['depth']:
                    print("Depth Testing")
                    appr = {"classifier": name,
                            "result": ai.mydata.target_data[
                                clf.predict(np.array([data['fe'], data['co'], data['depth']]).reshape(1, -1))[0]]
                            }
                    # os.system("say 'Classifier %s identifies object as %s'" % (name, ai.mydata.target_data[
                    #             clf.predict(np.array([data['fe'], data['co'], data['depth']]).reshape(1, -1))[0]]))
                else:
                    appr = {"classifier": name,
                            "result": ai.mydata.target_data[
                                clf.predict(np.array([data['fe'], data['co']]).reshape(1, -1))[0]]
                            }
                    # os.system("say 'Object identified as %s'" % ai.mydata.target_data[clf.predict(np.array([data['fe'],data['co']]).reshape(1, -1))[0]])
                results.append(json.dumps(appr))
            print(results)
            return '{"result": %s }' % json.dumps(results)
        elif data['button'] == 'retrain':
            retrain()
            return '{"result": "retrained" }'


    else:
        return send_from_directory('static', 'index.html')


def insert(fe, co, depth, id, category):
    with app.app_context():
        # g.db is the database connection
        query = 'INSERT INTO feco (fe, co, depth, id, category) VALUES (%s, %s, %s,"%s", "%s")' % (
        fe, co, depth, id, category)
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


def retrain():
    # os.system("say 'Matrix retraining'")
    dbdata = query_db("SELECT * from feco")
    print("Dumping DB")
    print(dbdata)
    for rec in dbdata:
        ai.mydata.da.append(list(rec))
    print(ai.mydata.da)
    ai.mydata.rebuild(l=4)
    ai.rebuild()


if __name__ == "__main__":
    try:
        init_db()
    except Exception, e:
        print("DB Already initialized")
    retrain()
    app.run(host='0.0.0.0', port=5000, debug=False)
