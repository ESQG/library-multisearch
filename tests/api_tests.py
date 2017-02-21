import unittest
import sys
# from bs4 import BeautifulSoup

sys.path.append('../')  # to import from parent directory
from queries import use_goodreads, use_sfpl, sfpl_locations

SHORT_SHELF = "https://www.goodreads.com/review/list/2416346?shelf=maybe-someday"
ESQG="2416346"

class QueryTests(unittest.TestCase):
    def test_get_shelf(self):
        data = use_goodreads.parse_shelf_and_id(SHORT_SHELF)
        print data
        shelf = data['shelf']
        goodreads_id = data['goodreads_id']
        results = use_goodreads.get_shelf(goodreads_id, shelf)
        self.assertIn('Asimov', str(results))
        self.assertEqual(type(results), list)
        self.assertGreater(len(results), 0)
        self.assertIn('author', results[0])
        print "First result:", results[0]


if __name__ == '__main__':
    unittest.main()