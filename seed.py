from bs4 import BeautifulSoup
import use_goodreads
from model import *
from server import app
from datetime import datetime

connect_to_db(app)

def add_my_toread_list():
    esqg = User(first_name="Elizabeth", last_name="Goodman", email="esqg@nowhere.com", password="programmer")
    db.session.add(esqg)
    db.session.commit()

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


def log_overlaps(title, author):

    search_author = author.split().strip(',')
    title_pieces = title.split()
    if title_pieces[0] == 'The' or title_pieces[0] == 'A' or title_pieces[0] == 'An':
        search_title = title_pieces[1]
    else:
        search_title = title_pieces[0]
    overlaps = Book.query.filter(Book.title.like('%' + search_title + '%'), Book.author.like('%' + search_author + '%'))

    if overlaps:
        with open('overlap-log.txt', 'a') as outfile:
            outfile.write(datetime.now().isoformat())
            outfile.write('\n')
            outfile.write("Found overlaps: ")
            outfile.write("%s by %s" % (title, author))
            outfile.write('\n')
            for book in overlaps:
                outfile.write('\t')
                outfile.write(str(book))
                outfile.write('\n')

def add_book(title, author):
    already_there = Book.query.filter_by(title=title, author=author).one()

    if already_there:
        return already_there

    log_overlaps(title, author)     # In case of non-exact matches, write log

    book = Book(title=title, author=author)
    db.session.add(book)
    db.session.commit()
    return book



