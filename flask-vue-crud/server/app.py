import uuid
from flask import Flask, jsonify, request
from flask_cors import CORS


BOOKS = [
    {
        'id': uuid.uuid4().hex,
        'title': 'On the Road',
        'author': 'Jack Kerouac',
        'read': True
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Harry Potter and the Philosopher\'s Stone',
        'author': 'J. K. Rowling',
        'read': False
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Green Eggs and Ham',
        'author': 'Dr. Seuss',
        'status': True
    }
]
SESSS = [
    {
        'id': uuid.uuid4().hex,
        'title': 'On the Road',
        'phone': 'Jack Kerouac',
        'status': True
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Harry Potter and the Philosopher\'s Stone',
        'phone': 'J. K. Rowling',
        'status': False
    },
    {
        'id': uuid.uuid4().hex,
        'title': 'Green Eggs and Ham',
        'phone': 'Dr. Seuss',
        'status': True
    }
]

# configuration
DEBUG = True

# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})


# sanity check route
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify('pong!')


def remove_book(book_id):
    for book in BOOKS:
        if book['id'] == book_id:
            BOOKS.remove(book)
            return True
    return False
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


@app.route('/books', methods=['GET', 'POST'])
def all_books():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        BOOKS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read')
        })
        response_object['message'] = 'Book added!'
    else:
        response_object['books'] = BOOKS
    return jsonify(response_object)

@app.route('/sesss', methods=['GET', 'POST'])
def all_sesss():
    response_object = {'status': 'success'}
    if request.method == 'POST':
        title = request.form['title'] if 'title' in request.form else "#"
        phone = request.form['phone'] if 'phone' in request.form else "#"
        post_data = request.get_json()
        SESSS.append({
            'id': uuid.uuid4().hex,
            'title': title,
            'phone': phone,
            'status': "0"
        })
        response_object['message'] = 'Sess added!'
    else:
        response_object['sesss'] = SESSS
    return jsonify(response_object)



@app.route('/books/<book_id>', methods=['PUT', 'DELETE'])
def single_book(book_id):
    response_object = {'status': 'success'}
    if request.method == 'PUT':
        post_data = request.get_json()
        remove_book(book_id)
        BOOKS.append({
            'id': uuid.uuid4().hex,
            'title': post_data.get('title'),
            'author': post_data.get('author'),
            'read': post_data.get('read')
        })
        response_object['message'] = 'Book updated!'
    if request.method == 'DELETE':
        remove_book(book_id)
        response_object['message'] = 'Book removed!'
    return jsonify(response_object)


if __name__ == '__main__':
    app.run()
