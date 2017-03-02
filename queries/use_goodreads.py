import os
import requests
import urlparse
import re
import urllib
from bs4 import BeautifulSoup


api_key = os.environ['GOODREADS_API_KEY']
api_secret = os.environ['GOODREADS_API_SECRET']

ESQG = "2416346"
BASE_URL = "https://www.goodreads.com/review/"
LIST_URL = BASE_URL+"list"


def parse_soup(soup):
    if type(soup) == int:
        return "Error: %s" % soup

    books = soup.find_all('book')
    return_books = []

    for book in books:
        title = book.title.text     # Issue: may have series numbers, could be problem?
        author = book.author.find('name').text      # Using .name returns 'author' i.e. tag label
        isbn = book.isbn.text
        return_books.append({'title': title, 'author':author, 'isbn':isbn})

    print "Books found:", len(return_books)
    return return_books


def soup_from_shelf(request_data):
    """Parse a list of books from the Goodreads API.  Returns a list of dictionaries,
    each one with keys 'title', 'author', and 'isbn'.

    So far this only works for books up to size 200."""

    assert request_data.get('v') == '2'    # Goodreads API mandates "&v=2"
    assert request_data.get('key') == api_key  # Need to include api key!
    assert 'shelf' in request_data    # Probably will return error without a shelf

    response = requests.get(LIST_URL, request_data)      # Goodreads returns XML only, JSON not allowed

    if response.status_code != 200:
        print "Error!", response.status_code
        return response.status_code

    return BeautifulSoup(response.content, "html.parser")
    

def parse_shelf_and_id(goodreads_link):
    if not goodreads_link:
        return {'shelf': None, 'goodreads_id': None}

    parsed = urlparse.urlparse(goodreads_link)
    if "goodreads.com" not in parsed.netloc:
        return {'shelf': None, 'goodreads_id': None}

    if parsed.query and "shelf=" in parsed.query:
        shelf_index = parsed.query.index("shelf=") + 6
        shelf = parsed.query[shelf_index:].split("&")[0]    # E.g. "shelf=to-read&a=b" --> "to-read"
    else:
        shelf = None

    goodreads_finder = re.search(r'\d{1,8}', goodreads_link)    # Returns None if no matches
    if goodreads_finder:
        goodreads_id = goodreads_finder.group()
    else:
        goodreads_id = None

    return {'shelf': shelf, 'goodreads_id': goodreads_id}


def get_shelf(goodreads_id, shelf):
    request_data = {'v':'2', 'id':goodreads_id, 'key':api_key, 'shelf':shelf, 'per_page':'200'}

    return parse_soup(soup_from_shelf(request_data))


def my_toread_list():
    shelf = 'to-read'
    goodreads_id = ESQG
    return get_shelf(goodreads_id, shelf)

