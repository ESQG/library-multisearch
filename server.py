from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension
from data.model import connect_to_db


app = Flask(__name__)

app.secret_key="ENID BLYTON"


@app.route("/")
def home_page():
    return render_template("home.html")

@app.route("/booklist", methods="POST")
    
    if 'goodreads-id' in request.form:
        session['goodreads_id'] = request.form['goodreads-id']
        session['bookshelf'] = "https://www.goodreads.com/review/list/" + goodreads_id + "?shelf=to-read"
    else:
        session['bookshelf'] = request.form.get('goodreads-link')

    # parse the url into shelf and goodreads id! / check if valid
    # send data! {'v':'2', 'id': goodreads_id, 'key':api_key, 'shelf':'to-read', 'per_page':'200'}
    # do the queries use_goodreads. Import above.

if __name__ == '__main__':
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")