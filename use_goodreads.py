import os
import requests
from bs4 import BeautifulSoup


api_key = os.environ['GOODREADS_API_KEY']
api_secret = os.environ['GOODREADS_API_SECRET']

ESQG = "2416346"
BASE_URL = "https://www.goodreads.com/review/"
LIST_URL = BASE_URL+"list"


def parse_list(request_data):
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

    soup = BeautifulSoup(response.content)
    books = soup.find_all('book')
    return_books = []

    for book in books:
        title = book.title.text     # Issue: may have series numbers, could be problem?
        author = book.author.find('name').text      # Using .name returns 'author' i.e. tag label
        isbn = book.isbn.text
        return_books.append({'title': title, 'author':author, 'isbn':isbn})

    print "Books found:", len(return_books)
    return return_books

def my_toread_list():
    sample_request_data = {'v':'2', 'id': ESQG, 'key':api_key, 'shelf':'to-read', 'per_page':'10'}
    return parse_list(sample_request_data)
