from flask import Flask, render_template, session, flash, redirect, request
from flask_debugtoolbar import DebugToolbarExtension
from data.model import connect_to_db
from queries import use_goodreads
from datetime import datetime

app = Flask(__name__)

app.secret_key="ENID BLYTON"


@app.route("/")
def home_page():
    return render_template("home.html")

@app.route("/booklist", methods=["POST"])
def display_books_from_form():

    if 'goodreads-id' in request.form:
        goodreads_id = request.form.get('goodreads-id')
        shelf = "to-read"
        write_log("Form submitted", str(goodreads_id), str(shelf))

    else:
        goodreads_link = request.form.get("goodreads-link")
        goodreads_data = use_goodreads.parse_shelf_and_id(goodreads_link)
        shelf = goodreads_data['shelf']
        goodreads_id = goodreads_data['goodreads_id']

    if shelf and goodreads_id:
        session.update({'shelf': shelf, 'goodreads_id': goodreads_id})
        write_log("Successful session", str(session))

    else:
        flash("Could not find a Goodreads bookshelf at that address. Please try again.")
        write_log("Goodreads unsuccessful", "shelf: " + str(shelf), "goodreads_id: " + str(goodreads_id))
        return redirect("/")

    books = use_goodreads.get_shelf(session['goodreads_id'], session['shelf'])

    session['books'] = books
    write_log("Books added to session", str(books)[:100])
    return render_template("books.html", books=books)

@app.route("/booklist", methods=["GET"])
def display_books_from_session():

    if 'books' in session:
        books = session['books']
        return render_template("books.html", books=books)
    else:
        write_log("No books found in session", str(session)[:200])
        flash("Sorry, we have no books for you yet. Please provide a bookshelf.")
        return redirect("/")


def write_log(*args):
    with open("notes/server.log", 'a') as log_file:
        log_file.write(datetime.now().isoformat() + "\t")
        log_file.write("\n".join(args))
        log_file.write("\n")

if __name__ == '__main__':
    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")