from flask import Flask, render_template, session, flash, redirect, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from datetime import datetime
import os

from data.seed import SFPL_BRANCHES
from data import data_manager
from queries import use_goodreads

GOOGLEMAPS_KEY = os.environ["GOOGLEMAPS_API_KEY"]
app = Flask(__name__)
# app.config['TEMPLATES_AUTO_RELOAD'] = True

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

        write_log("Successful session", str(session)[:200])

    else:
        flash("Could not find a Goodreads bookshelf at that address. Please try again.")
        write_log("Goodreads unsuccessful", "shelf: " + str(shelf), "goodreads_id: " + str(goodreads_id))
        return redirect("/")

    books = use_goodreads.get_shelf(session['goodreads_id'], session['shelf'])
    books.sort(key=lambda x: x['author'])

    book_ids = []   # For database
    for book_data in books:
        book = data_manager.add_book(book_data['title'], book_data['author'])
        book_ids.append(book.book_id)

    session['books'] = book_ids
    session.modified = True     # Make sure FLask updates the session cookie! Had issues with this

    write_log("Books added to session", str(session)[:200])
    return redirect('/booklist')

@app.route("/booklist", methods=["GET"])
def display_books_from_session():

    if 'books' in session:
        book_ids = session['books']

        books = data_manager.get_books(book_ids)
        return render_template("books.html", books=books)

    else:
        write_log("No books found in session", str(session)[:200])
        flash("Sorry, we have no books for you yet. Please provide a bookshelf.")
        return redirect("/")


@app.route("/books.json")
def show_branches_and_bookids():
    branches = data_manager.branch_dict_list("sfpl")
    avg_lat = 37.75774
    avg_long = -122.43870
    bounds = {'lat': [-122.54, -122.35], 'lng': [37.67, 37.84]}
    center = {'lat': avg_lat, 'lng': avg_long}


    data_to_serve = {'branches': branches,
                     'map_center': center,
                     'map_bounds': bounds,
                     }

    if 'books' in session:
        data_to_serve['book_ids'] = session['books']
    else:
        data_to_serve['book_ids'] = []
    return jsonify(data_to_serve)

@app.route("/book/<book_id>.json")
def book_info(book_id):
    """Serve a JSON object of records associated with the book, along with stored availability."""

    book = data_manager.get_book(book_id)
    if not book:
        return jsonify({'book_id': None, 'records': None})

    records = data_manager.get_stored_availability(book)
    
    if not records:     # If availability is not in the database, otherwise it's []
        unchecked_records = data_manager.records_from_book(book)
        records = []
        for record in unchecked_records:
            data_manager.update_availability(record)

        records = data_manager.get_stored_availability(book)

    return jsonify({'book_id': book_id, 
                    'title': book.title, 
                    'author': book.author, 
                    'records': records})

@app.route("/librarybooks")
def library_books_page():

    codes_and_names = sorted(SFPL_BRANCHES.items(), key=lambda tup: tup[1])
    return render_template("library_books.html", codes_and_names=codes_and_names, map_key=GOOGLEMAPS_KEY)


def write_log(*args):
    """Each argument in args must be a string.  This will write to the file notes/server.log,
    with a timestamp preceding args.  If you see strangely cut off data, like an incomplete
    dictionary, it's because the code above only logs a few hundred characters of objects that 
    might be long."""

    with open("notes/server.log", 'a') as log_file:
        log_file.write(datetime.now().isoformat() + "\t")
        log_file.write("\n".join(args))
        log_file.write("\n")

if __name__ == '__main__':
    from data.model import connect_to_db

    app.debug = True

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host="0.0.0.0")