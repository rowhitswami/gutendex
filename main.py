from gutendex import Queries
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin
from gevent.pywsgi import WSGIServer

# Creating Flask app 
app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

def format_values(data):
    """
    Return parsed values of the request
    """
    return [data_value.strip() for data_value in data.split(',')] if data else []

@app.route('/get_books', methods=["POST"])
@cross_origin()
def get_books():
    """
    POST Method to return books corresponding the the query
    """
    topics = format_values(request.form.get('topics'))
    authors = format_values(request.form.get('authors'))
    book_ids = format_values(request.form.get('book_ids'))
    titles = format_values(request.form.get('titles'))
    languages = format_values(request.form.get('languages'))
    mime_types = format_values(request.form.get('mime_types'))
    page = format_values(request.form.get('page'))
    page = int(page[0]) if page else 1
    status, data = Queries().search_books(book_ids, languages, mime_types,
                                          authors, titles, topics, page)
    if status:
        books, count, page, total_page = data
        return jsonify({'count': count, 'page': page, 'total_page': total_page, 'books': books}), 200
    else:
        return jsonify({'error': data}), 400

# Serving the app forever, or till my AWS free quota exhausts
if __name__ == "__main__":
    http_server = WSGIServer(('', 5000), app)
    print(f"Serving at {http_server}")
    http_server.serve_forever()
