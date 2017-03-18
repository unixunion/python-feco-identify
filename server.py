import json
import logging
import sqlite3
import hashlib
from logging.handlers import RotatingFileHandler
import os
import numpy as np
from flask import Flask, request, send_from_directory, g, redirect, session, render_template
import uuid
from flask import url_for
from flask_mail import Mail, Message
import time
import random

from werkzeug.utils import secure_filename

from ai import Matrix

DATABASE = 'database.db'

LOGFORMAT = '%(asctime)-15s [%(username)s] %(filename)s %(module)s:%(lineno)d - %(message)s'

ai_sessions = {}

# set the project root directory as the static folder, you can set others.
app = Flask(__name__, static_url_path='')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME=os.environ['GUN'],
    MAIL_PASSWORD=os.environ['GPW'],
    UPLOAD_FOLDER=UPLOAD_FOLDER
)
mail = Mail(app)




# Custom logging
class ContextFilter(logging.Filter):
    """
    This is a filter which injects contextual information into the log.
    """

    def filter(self, record):
        # with app.app_context():
        try:
            record.username = session['username']
            return True
        except KeyError, e:
            record.username = "NOT LOGGED IN"
            return True


# checks a obj is not none or a ""
def notnull(name, obj):
    app.logger.info("checking %s object %s is not None or ''" % (name, obj))
    if obj is not None and obj is not '' and obj is not u"" and obj is not u'':
        return
    else:
        app.logger.debug("%s is not set" % name)
        raise Exception("%s is empty" % name)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login Route

    Checks auth, and sets up server-side session for user. Handles both GET and POST for presenting
    the login page, and handling the page posts.

    Also creates the instances of the AI on the server side, in the ai_sessions dictionary

    :return: login page, or result of login
    """
    if request.method == 'POST':
        try:
            data = request.get_json(force=True)
            app.logger.info("user login request with data: %s" % data)
            if check_auth(data['username'], data['password']):
                app.logger.info("%s, login success" % data['username'])
                session['username'] = data['username']
                ai_sessions["%s-ai" % session['username']] = Matrix(l=3, max_features=3)
                ai_sessions["%s-ai2" % session['username']] = Matrix(l=3, max_features=2)
                try:
                    retrain_session(u'')
                except Exception, e:
                    return '{"result": "ok"}', 200
                return '{"result": "ok"}', 200
            else:
                app.logger.error("error logging in with data: %s" % data)
                return '{"result": "Authentication Failure"}', 401
        except Exception, e:
            app.logger.error("error: %s" % e)
            return '{"result": "Server Error"}', 500
    else:
        app.logger.debug("get request, returning login page")
        return render_template('login.html')


@app.route('/logout')
def logout():
    """
    Logout removes the username from the server-side session, and nukes the AI's for the session
    :return:
    """
    try:
        app.logger.info("initiating logout: %s" % session['username'])
        ai_sessions.pop("%s-ai" % session['username'], None)
        ai_sessions.pop("%s-ai2" % session['username'], None)
    except Exception, e:
        app.logger.error("logout could not shutdown AI's, %s" % e.message)

    try:
        session.pop('username', None)
    except KeyError, e:
        app.logger.error("user is not logged in, %s" % e.message)

    app.logger.info("successfully logged out")
    return redirect("/login")

def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    pw224 = hashlib.sha224(password).hexdigest()
    # return username == 'keghol' and password == 'co1n'
    dbdata = query_db(
        "SELECT email, password FROM users WHERE email = '%s' AND password = '%s' AND isactive = 1" % (username, pw224))
    if dbdata:
        return True
    else:
        return False

# new user registration
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        app.logger.info("registration attempt")
        try:
            data = request.get_json(force=True)

            try:
                notnull("token", data["token"])
                commit_db("UPDATE users SET password = '%s' WHERE emailhash='%s'" % (hashlib.sha224(data['password']).hexdigest(), data["token"]))
                return '{"result": "reset"}', 200

            except Exception, e:

                notnull("username", data["username"])
                notnull("password", data["password"])
                token = random.getrandbits(128)
                query = 'INSERT INTO users (isactive, email, emailhash, password) VALUES (0, "%s", "%s", "%s")' % (
                    data['username'], token, hashlib.sha224(data['password']).hexdigest())
                cur = get_db().execute(query)
                get_db().commit()
                app.logger.info("user specifics: %s" % data)
                activationemail(data['username'], token)
                return '{"result": "ok"}', 200
        except Exception, e:
            app.logger.error("error registering user, %s" % e.message)
            return '{"result": "error"}', 401
    else:
        # return send_from_directory('static', 'register.html')
        return render_template('register.html')


# initiate lost password process
@app.route("/lostpass", methods=['POST'])
def lostpass():
    if request.method == "POST":
        app.logger.info("lostpassword request")
        try:
            data = request.get_json(force=True)
            notnull("username", data["username"])
            token = random.getrandbits(128)
            commit_db("UPDATE users SET emailhash = '%s' WHERE email='%s'" % (token, data["username"]))
            app.logger.info("token updated for username %s" % data["username"])
            lostpasswordemail(data["username"], token)
            return '{"result": "ok"}', 200

        except Exception, e:
            app.logger.error("error initiating password recovery for data: %s, error was: %s" % (data, e.message))
            return '{"result": "error"}', 500


@app.route("/passwordreset/<string:token>", methods=['GET'])
def passwordrecovery(token):
    app.logger.info("password reset")
    try:
        # data = request.get_json(force=True)
        notnull("token", token)
        dbdata = query_db(
            "SELECT rowid,email FROM users WHERE emailhash = '%s'" % token)
        time.sleep(2)
        if dbdata:
            return render_template("register.html", token=token)
        else:
            return render_template("register.html")
    except Exception, e:
        app.logger.error("password reset failed: %s" % e)
        return render_template("register.html")


@app.route("/activateuser/<string:hash>", methods=['GET'])
def activateuser(hash):
    app.logger.info("activating user with hash: %s" % hash)
    dbdata = query_db("SELECT rowid FROM users WHERE emailhash = '%s'" % hash)
    app.logger.info("activate user %s" % dbdata)
    app.logger.info(dbdata)

    if dbdata:
        app.logger.info("success")
        query = 'UPDATE users SET isactive = 1 WHERE rowid = "%s"' % dbdata[0]
        cur = get_db().execute(query)
        get_db().commit()
        cur.close()
        return redirect("/")
    else:
        app.logger.info("error")
        return redirect("/")


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/upload", methods=["POST"])
def upload():
    if request.method=="POST":
        app.logger.debug("upload request")
        if 'file' not in request.files:
            return json.dumps({"result": "no file"})
        else:
            file = request.files['file']
            if file.filename == '':
                return json.dumps({"result": "no file name"})
            if file and allowed_file(file.filename):
                filename = secure_filename(session["username"] +"-"+ str(uuid.uuid1()) + "-" + file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                # return redirect(url_for('uploaded_file',
                #                         filename=filename))
                return json.dumps({"result": url_for('uploaded_file', filename=filename)})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

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


@app.route("/dbdump")
def dbdump():
    app.logger.info("dbdump request")
    try:
        dbdata = query_db(
            "SELECT rowid, fe, co, depth, id, category, fieldid, latitude, longitude from feco WHERE userid IS '%s' ORDER BY rowid DESC" %
            session['username'])
        app.logger.info("dumping database contents")
        app.logger.info(dbdata)
        return json.dumps(dbdata)
    except Exception, e:
        return json.dumps(
            [(1, "error", "error", "error", "Error: %s" % e.message, "Unable to query database", 'dbdump')])


@app.route("/delete/<int:rowid>")
def delete(rowid):
    app.logger.info("request to delete record %s" % rowid)
    try:
        commit_db('DELETE FROM feco where ROWID = "%s" AND USERID = "%s"' % (rowid, session['username']))
        return json.dumps({"result": "ok"})
    except Exception, e:
        return json.dumps({"result": e.message})


@app.route("/ids")
def ids():
    app.logger.info("getting ids")
    l = {}
    try:
        for k in ai_sessions["%s-ai" % session['username']].mydata.target_names:
            l[k] = None
        return json.dumps(l)
    except Exception, e:
        app.logger.error("error getting ids: %s" % e.message)
        return redirect("/login")


@app.route("/fields")
def fields():
    app.logger.info("getting fields")
    fl = {}
    try:
        list_fields = query_db('Select DISTINCT fieldid from feco WHERE userid IS "%s"' % session['username'])
        app.logger.info("db returned list of fields: %s" % list_fields)
        for f in list_fields:
            fl[f[0]] = None
        return json.dumps(fl)
    except Exception, e:
        app.logger.error("error getting fields: %s" % e.message)
        return redirect("/login")


@app.route("/fieldlist")
def fieldlist():
    app.logger.info("getting fieldlist")
    fl = []
    fl.append("All Fields")
    try:
        list_fields = query_db('Select DISTINCT fieldid from feco WHERE userid IS "%s"' % session['username'])
        app.logger.info("db returned list of fields: %s" % list_fields)
        for f in list_fields:
            fl.append(f)
        return json.dumps(fl)
    except Exception, e:
        app.logger.error("error getting field list: %s" % e.message)
        return redirect("/login")


@app.route("/categories")
def categories():
    l = {}
    try:
        for k in ai_sessions["%s-ai" % session['username']].mydata.target_data:
            l[k] = None
        return json.dumps(l)
    except Exception, e:
        app.logger.error("error retrieving categories, %s" % e.message)
        return redirect("/login")


def activationemail(email, token):
    msg = Message(
        'Deblox Intelligence Activation',
        sender='vendors@kegans.com',
        recipients=
        [email])
    msg.body = render_template("mail.html", email=email, token=token)
    mail.send(msg)
    return "Sent"


def lostpasswordemail(email, token):
    msg = Message(
        'Deblox Intelligence Lost Password',
        sender='vendors@kegans.com',
        recipients=
        [email])
    msg.body = render_template("lostpassword.html", email=email, token=token)
    mail.send(msg)
    return "Sent"


@app.route("/", methods=['GET', 'POST'])
def root():
    app.logger.info("Root")
    if 'username' in session:
        app.logger.info("User %s is logged in" % session['username'])
        try:
            notnull("ai", ai_sessions["%s-ai" % session['username']])
            notnull("ai2", ai_sessions["%s-ai2" % session['username']])
        except Exception, e:
            return redirect("/login")

        if request.method == 'POST':
            # app.logger.info("post")
            data = request.get_json(force=True)
            app.logger.info(data)

            if (data['button'] == 'record'):
                try:
                    notnull("fe", data['fe'])
                    notnull("co", data['co'])
                    notnull("depth", data['depth'])
                    notnull("name", data['id'])
                    notnull("category", data['category'])
                    notnull("field", data['field'])
                    app.logger.info("Recording findings: %s" % data)
                    try:
                        insert(data['fe'], data['co'], data['depth'], data['id'], data['category'], session['username'],
                               data['field'], data['latitude'], data['longitude'])
                    except Exception, e:
                        return '{"result": "error: %s}' % e
                    retrain_session(data['field'])
                    return '{"result": "ok"}'
                except Exception, e:
                    return '{"result": "error, %s" }' % e.message
            elif (data['button'] == 'guess'):

                results = []
                appr = {}

                try:
                    app.logger.info("Guessing: %s" % data)
                    notnull("fe", data['fe'])
                    notnull("co", data['co'])

                    if data['depth']:
                        for name, clf in ai_sessions["%s-ai" % session['username']].compiled_classifiers:
                            app.logger.info("Depth set, so 3 feature testing")
                            appr = {"classifier": name,
                                    "result": ai_sessions["%s-ai" % session['username']].mydata.target_data[
                                        clf.predict(np.array([data['fe'], data['co'], data['depth']]).reshape(1, -1))[
                                            0]]
                                    }
                            results.append(json.dumps(appr))
                    else:
                        for name, clf in ai_sessions["%s-ai2" % session['username']].compiled_classifiers:
                            app.logger.info("2 feature testing")
                            appr = {"classifier": name,
                                    "result": ai_sessions["%s-ai2" % session['username']].mydata.target_data[
                                        clf.predict(np.array([data['fe'], data['co']]).reshape(1, -1))[0]]
                                    }
                            results.append(json.dumps(appr))
                    app.logger.info(results)
                    return '{"result": %s }' % json.dumps(results)
                except Exception, e:
                    app.logger.info("fe/co not set")
                    results.append(json.dumps({"result": "%s" % e.message}))
                    return '{"result": %s }' % json.dumps(results)
            elif data['button'] == 'retrain':
                try:
                    # notnull("field", data['field'])
                    retrain_session(data['field'])
                    if not data['field'] or data['field'] == u'All Fields':
                        return '{"result": "retrained for All Fields"}'
                    else:
                        return '{"result": "retrained for field: %s" }' % data['field']
                except Exception, e:
                    return '{"result": "error retraining %s" }' % e.message


        else:
            # return send_from_directory('static', 'index.html')
            return render_template('index.html', username=session['username'])
    else:
        app.logger.info("unknown user")
        return redirect("/login")


# write a find to the db
def insert(fe, co, depth, id, category, userid, field, latitude, longitude):
    with app.app_context():
        # g.db is the database connection
        query = 'INSERT INTO feco (fe, co, depth, id, category, userid, fieldid, latitude, longitude) VALUES (%s, %s, %s,"%s", "%s", "%s", "%s", %s, %s)' % (
            fe, co, depth, id, category, userid, field, latitude, longitude)
        cur = get_db().execute(query)
        # cur.execute(query, values)
        get_db().commit()
        # id = cur.lastrowid
        cur.close()
        return id


# select something from the DB
def query_db(query, args=(), one=False):
    with app.app_context():
        cur = get_db().execute(query, args)
        rv = cur.fetchall()
        cur.close()
        return (rv[0] if rv else None) if one else rv


# commit something to DB
def commit_db(query, args=(), one=False):
    with app.app_context():
        cur = get_db().execute(query, args)
        get_db().commit()
        cur.close()


# retrains the AI for the selected field
def retrain_session(field):
    app.logger.info('Retraining, field is %s' % field)
    with app.app_context():
        dbdata = []
        if field is u'' or field == u'All Fields':
            app.logger.info("Global Field selected, loading all datasets")
            dbdata = query_db("SELECT fe, co, depth, id, category from feco WHERE userid IS '%s'" % session['username'])
        else:
            app.logger.info("Specific Field: %s selected, loading limited dataset" % field)
            dbdata = query_db(
                "SELECT fe, co, depth, id, category from feco WHERE userid IS '%s' AND fieldid IS '%s'" % (
                    session['username'], field))

        app.logger.info("dumping DB contents")
        app.logger.info(dbdata)

        # new AI sessions
        app.logger.info("instantiate matricies")
        ai_sessions["%s-ai" % session['username']] = Matrix(l=3, max_features=3)
        ai_sessions["%s-ai2" % session['username']] = Matrix(l=3, max_features=2)

        app.logger.info("iterating over dataset and appending to Matrices")
        for rec in dbdata:
            ai_sessions["%s-ai" % session['username']].mydata.da.append(list(rec))
            ai_sessions["%s-ai2" % session['username']].mydata.da.append(list(rec))

        app.logger.info("dumping ai dataset")
        app.logger.info(ai_sessions["%s-ai" % session['username']].mydata.da)

        app.logger.info("dumping ai2 dataset")
        app.logger.info(ai_sessions["%s-ai2" % session['username']].mydata.da)

        app.logger.info("rebuilding both 2nd and 3rd dimensional ai for datasets")
        ai_sessions["%s-ai" % session['username']].mydata.rebuild(l=4)
        ai_sessions["%s-ai" % session['username']].rebuild()
        ai_sessions["%s-ai2" % session['username']].mydata.rebuild(l=4)
        ai_sessions["%s-ai2" % session['username']].rebuild()
        app.logger.info("ai retrained successfully")


# creates the initial schema
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# creates user schema
def create_users():
    with app.app_context():
        db = get_db()
        with app.open_resource('users.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


if __name__ == "__main__":

    handler = RotatingFileHandler('server.log', maxBytes=100000000, backupCount=5)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(LOGFORMAT)
    handler.setFormatter(formatter)
    handler.addFilter(ContextFilter())
    app.logger.addHandler(handler)

    try:
        init_db()
    except Exception, e:
        print("DB Already initialized: %s" % e.message)

    try:
        create_users()
    except Exception, e:
        print("Users table already created: %s" % e.message)

    # retrain()
    app.run(host='0.0.0.0', port=5000, ssl_context=('server.key.crt', 'server.key.key'))
