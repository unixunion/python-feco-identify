import logging
import sqlite3
from flask import Flask, request, send_from_directory, g
import ai
import numpy as np
import json

# data = datasets.s()

DATABASE = 'database.db'

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


@app.route("/", methods=['GET', 'POST'])
def root():
    if request.method == 'POST':
        print("post")
        data = request.get_json(force=True)
        print(data['fe'])

        if (data['button']=='record'):
            print("Recording findings")
            return '{"result": "ok"}'
        else:
            print("Guessing")
            results = []
            for clf in ai.compiled_classifiers:
                results.append(ai.mydata.target_data[clf.predict(np.array([data['fe'],data['co']]).reshape(1, -1))[0]])
            print(results)
            return '{"result": %s }' % json.dumps(results)

    else:
        return send_from_directory('static', 'index.html')


def insert(fe, co, id):
    # g.db is the database connection
    query = 'INSERT INTO feco (fe, co, id) VALUES (%s, %s, "%s")' % (fe, co, id)
    cur=get_db().execute(query)
    # cur.execute(query, values)
    get_db().commit()
    # id = cur.lastrowid
    cur.close()
    return id


def query_db(query, args=(), one=False):
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


if __name__ == "__main__":
    # init_db()

    app.run()
