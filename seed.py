from bs4 import BeautifulSoup
import use_goodreads
from model import *
from server import app
from datetime import datetime
import data_manager

connect_to_db(app)

def sfpl_branches():
    sfpl = LibrarySystem(library_code="sfpl", name="San Francisco Public Library")
    db.session.add(sfpl)
    pass



def add_my_toread_list():
    esqg = User(first_name="Elizabeth", last_name="Goodman", email="esqg@nowhere.com", password="programmer")
    db.session.add(esqg)
    db.session.commit()
    goodreads = GoodreadsUser(user_id=esqg.user_id, goodreads_id="2416346")

    with open('stuff2.xml', 'r') as esqg_toread_file:
        book_list_soup = BeautifulSoup(esqg_toread_file.read(), "html.parser")

    book_list = use_goodreads.parse_soup(book_list_soup)

    for book_data in book_list:
        book = Book(title=book_data['title'], author=book_data['author'])
        db.session.add(book)
        db.session.commit()


        assoc = UserBook(book_id = book.book_id, user_id = esqg.user_id)
        db.session.add(assoc)
        db.session.commit()






