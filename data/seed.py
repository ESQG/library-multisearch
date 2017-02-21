# Outside packages and standard libraries
from bs4 import BeautifulSoup
from datetime import datetime
import sys

# Local imports
from model import *
import data_manager

# Parent directory imports protected under ifmain.

SFPL_BRANCHES = {
        'anza': 'Anza',
        'bayvw': 'Bayview',
        'bernal': 'Bernal Heights',
        'chtown': 'Chinatown',
        'eureka': 'Eureka Valley',
        'excel': 'Excelsior',
        'glenpk': 'Glen Park',
        'ggval': 'Golden Gate Valley',
        'ingles': 'Ingleside',
        'main': 'Main Library',
        'marina': 'Marina',
        'merced': 'Merced',
        'miss': 'Mission',
        'missb': 'Mission Bay',
        'noeval': 'Noe Valley',
        'nbeach': 'North Beach',
        'ocvw': 'Ocean View',
        'ortega': 'Ortega',
        'park': 'Park',
        'potr': 'Potrero',
        'presid': 'Presidio',
        'rich': 'Richmond',
        'sunset': 'Sunset',
        'visit': 'Visitacion Valley',
        'wport': 'West Portal',
        'wadd': 'Western Addition',
        'pside': 'Parkside',
        'portl': 'Portola',
    }



def add_formats():
    """Add standardized book formats to the database.

    Because of the dependency of the records table on this one,
    this function must be run when the database is created."""

    book_format = Format(format_code='book', name='Book', digital=False)
    db.session.add(book_format)

    ebook_format = Format(format_code='ebook', name='Downloadable ebook', digital=True)
    db.session.add(ebook_format)

    audio_cd = Format(format_code='audiocd', name='Audiobook CD', digital=False)
    db.session.add(audio_cd)

    large_print = Format(format_code='large', name='Large Print', digital=False)
    db.session.add(large_print)

    audio_digital = Format(format_code='eaudio', name='Downloadable Audiobook', digital=True)
    db.session.add(audio_digital)

    hoopla_format = Format(format_code='hoopla', name='Hoopla Digital Audiobook', digital=True)
    db.session.add(hoopla_format)

    db.session.commit()



def add_my_toread_list():
    """A function for my own debugging purposes.  It relies on my previously downloaded Goodreads response data."""


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

        assoc = UserBook(book_id=book.book_id, user_id=esqg.user_id)
        db.session.add(assoc)
        db.session.commit()


def add_sfpl_branches():
    """Adds the SFPL library system and the branches of it to the database.
    Because the data collected for SFPL catalog records depends on these branches,
    this function must be run for the server to operate properly."""

    sfpl = LibrarySystem(library_code='sfpl', name='San Francisco Public Library')
    db.session.add(sfpl)
    db.session.commit()

    for code in SFPL_BRANCHES:
        library = Branch(library_code='sfpl', branch_code=code, name=SFPL_BRANCHES[code])
        db.session.add(library)

    db.session.commit()


if __name__ == '__main__':
    # Parent directory imports
    sys.path.append('../')
    from queries import use_goodreads
    from server import app

    connect_to_db(app)


