"""Testing file!  Needs lots of work: have to do mock APIs."""

import unittest
import sys
from flask import Flask, request, session
from bs4 import BeautifulSoup
import json

sys.path.append('../')  # to import from parent directory
import server
from server import app
from data.model import *
from data import seed
from queries import use_goodreads, use_sfpl, sfpl_locations

SHORT_SHELF = "https://www.goodreads.com/review/list/2416346?shelf=maybe-someday"
ESQG = "2416346"

def _mock_get_shelf(goodreads_id, shelf):
    print "Using mock Goodreads scraper!"
    soup = BeautifulSoup(open("gr_response.xml"), "html.parser")
    return use_goodreads.parse_soup(soup)

    # change later to deal with short shelf!

server.use_goodreads.get_shelf = _mock_get_shelf


class QueryHelperTests(unittest.TestCase):
    """Test helper functions for the Queries files."""

    def test_shelf_parser(self):
        results = use_goodreads.parse_shelf_and_id(SHORT_SHELF)
        self.assertEqual(results['goodreads_id'], ESQG)
        self.assertEqual(results['shelf'], "maybe-someday")


    def test_parser_bad_shelves(self):
        empty_results = {'shelf': None, 'goodreads_id': None}

        link = "http://purple.com"
        results = use_goodreads.parse_shelf_and_id(link)
        self.assertEqual(results, empty_results)

        link = "12345"
        results = use_goodreads.parse_shelf_and_id(link)
        self.assertEqual(results, empty_results)

        results = use_goodreads.parse_shelf_and_id(None)
        self.assertEqual(results, empty_results)


class DataTests(unittest.TestCase):
    """Test functions from the data files."""

    def setUp(self):
        app.config['Testing'] = True
        connect_to_db(app, db_uri='postgresql:///testdb', echo=False)
        db.create_all()

        seed.add_sfpl_branches()
        example_data()


    def tearDown(self):
        db.session.close()
        db.drop_all()


class RouteAndDataTests(unittest.TestCase):
    """Test routes, integrated with database."""

    def setUp(self):
        """Creates test client, connects the server to test database, and populates sample data."""

        self.client = app.test_client()
        app.config['Testing'] = True
        app.config['SECRET_KEY'] = 'test'
        connect_to_db(app, db_uri='postgresql:///testdb', echo=False)
        db.create_all()

        example_data()          # Need to expand!
        

    def tearDown(self):
        """Removes all data from the test database."""

        db.session.close()
        db.drop_all()


    def test_homepage(self):
        """Tests the homepage loads."""

        response = self.client.get("/")
        self.assertIn("Books</title>", response.data)
        self.assertIn("Goodreads ID", response.data)


    def test_booklist_post(self):
        """Tests results of submitting Goodreads POST data.

        If the books are not successfully added to the session, the server
        will redirect to the homepage, so this tests that success.  

        This also tests that the books from the mock Goodreads API have been added 
        to the database, and that their IDs are in the session."""

        response = self.client.post("/booklist", data={'goodreads-id':ESQG}, follow_redirects=True)
        self.assertIn("View my books in the library", response.data)

        book = Book.query.filter_by(title="Postcards from the Edge").first()
        self.assertIsNotNone(book)

        with self.client.session_transaction() as sess:
            self.assertIn('books', sess)
            self.assertIn(book.book_id, sess['books'])
            self.assertIn('goodreads_id', sess)
            self.assertEqual(sess['goodreads_id'], ESQG)


    def test_booklist_post_link(self):
        response = self.client.post("/booklist", data={'goodreads-link': SHORT_SHELF}, follow_redirects=True)
        self.assertIn("View my books in the library", response.data)


    def test_booklist_get(self):
        with self.client.session_transaction() as sess:
            sess['books'] = [1, 2]

        response = self.client.get("/booklist")
        self.assertIn("View my books in the library", response.data)


    def test_booklist_json(self):
        with self.client.session_transaction() as sess:
            sess['books'] = [1, 2]        

        response = self.client.get("/books.json")
        self.assertEqual(response.status_code, 200)
        results = json.loads(response.data)

        self.assertIn('branches', results)
        self.assertIn('book_ids', results)

        self.assertIn(1, results['book_ids'])
        self.assertIn('main', results['branches'])


    def test_empty_booklist(self):
        response = self.client.get("/booklist", follow_redirects=True)
        self.assertIn("no books", response.data)





def example_data():
    """Data for the test database.  Runs in setUp functions for tests that use it."""

    seed.add_sfpl_branches()
    seed.add_formats()

    book_1 = Book(title="Alanna: The First Adventure", author="Tamora Pierce")
    book_2 = Book(title="The Hitchhiker's Guide to the Galaxy", author="Douglas Adams")
    db.session.add(book_1, book_2)

    esqg = User(first_name="Elizabeth", last_name="Goodman", email="esqg@nowhere.com", password="programmer")
    db.session.add(esqg)
    db.session.commit()

    esqg_gr = GoodreadsUser(user_id=esqg.user_id, goodreads_id=ESQG)
    db.session.add(esqg_gr)

    my_mission = UserBranch(branch_code="miss", user_id=esqg.user_id)
    db.session.add(my_mission)

    my_main = UserBranch(branch_code="main", user_id=esqg.user_id)
    db.session.add(my_main)

    db.session.commit()


if __name__ == '__main__':
    unittest.main()
