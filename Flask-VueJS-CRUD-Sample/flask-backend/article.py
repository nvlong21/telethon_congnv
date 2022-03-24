from flask import Flask, request, jsonify, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from datetime import datetime
from flask_cors import CORS
import json
import os

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

CORS(app)

UPLOAD_FOLDER = 'images/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sess.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)

class Sess(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000), unique=True)
    content = db.Column(db.String(1000))
    thumbnail = db.Column(db.String(1000))
    date_updated = db.Column(db.DateTime, nullable=False,
                    default=datetime.now())
    date_created = db.Column(db.DateTime, nullable=False,
                    default=datetime.now())

    def __init__(self, title, content, thumbnail, date_updated, date_created):
        self.title = title
        self.content = content
        self.thumbnail = thumbnail
        self.date_updated = date_updated
        self.date_created = date_created

class SessSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('id', 'title', 'content', 'thumbnail', 'date_updated', 'date_created')


sess_schema = SessSchema()
sesss_schema = SessSchema(many=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def message_fail(message):
    return json.dumps({'success': False, 'message': message}), 200, {'ContentType': 'application/json'}

# get images
@app.route("/images/<name>", methods=["GET"])
def get_image(name):
    path = os.getcwd() + '/images/'
    if os.path.isfile(path + name):
       filename = path + name
    else:
       filename = path + 'error.jpeg'
    return send_file(filename, mimetype='image/jpeg')

# upload image
def upload_image(data):
    if 'file' not in data:
        message_fail('No file uploaded')
    file = data['file']
    if file.filename == '':
        message_fail('File doesnt have name!')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'http://' + request.host + '/images/' + filename

# endpoint to create new sess
@app.route("/sess", methods=["POST"])
def add_sess():
    title = request.form['title']
    content = request.form['content']
    thumbnail = upload_image(request.files)
    date_updated = datetime.now()
    date_created = datetime.now()
    new_sess = Sess(title, content, thumbnail, date_updated, date_created)

    db.session.add(new_sess)
    db.session.commit()

    return json.dumps({'success': True, 'message': 'Data has been saved'}), 200, {'ContentType': 'application/json'}

# endpoint to show all sess
@app.route("/sess", methods=["GET"])
def get_sess():
    all_sesss = Sess.query.all()
    result = sesss_schema.dump(all_sesss)
    return jsonify(result.data)

# endpoint to get sess detail by id
@app.route("/sess/<id>", methods=["GET"])
def sess_detail(id):
    sess = Sess.query.get(id)
    return sess_schema.jsonify(sess)


# endpoint to update sess
@app.route("/sess/<id>", methods=["PUT", "PATCH"])
def sess_update(id):
    sess = Sess.query.get(id)
    sess.title = request.form['title'] if 'title' in request.form else sess.title
    sess.content = request.form['content'] if 'content' in request.form else sess.content
    sess.thumbnail = upload_image(request.files) if 'file' in request.files else sess.thumbnail
    sess.date_updated = datetime.now()
    sess.date_created = sess.date_created
    
    db.session.commit()
    return sess_schema.jsonify(sess)


# endpoint to delete sess
@app.route("/sess/<id>", methods=["DELETE"])
def sess_delete(id):
    sess = Sess.query.get(id)
    status = db.session.delete(sess)
    db.session.commit()

    if status == None:
        os.remove(os.getcwd() + '/images/' + sess.thumbnail.split('/')[-1])
    return sess_schema.jsonify(sess)


if __name__ == '__main__':
    app.run(debug=True)
