from flask import Flask, render_template
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db


app = Flask(__name__)

app.secret_key="ENID BLYTON"

if __name__ == '__main__':
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")