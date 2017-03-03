import requests
from bs4 import BeautifulSoup
import re

# Local imports
import sfpl_locations

BASE_URL = "https://sfpl.bibliocommons.com"

example = BASE_URL + "/search?custom_query=" + "title%3AFledgling+author%3AOctavia+Butler"


# Bibliocommons recommends 'contributor' in its construction form, should I use that?
def search_all_records(title, author):
    """Returns a list of dictionaries, basically scraping together my own API from the library catalog.  Attributes I pull out
    are the title, author, and format as listed on the search results page, along with the local link to the actual record.

    Empty list if no records found; otherwise, each record should be formatted like so:
    {'author': u'Tolkien, J. R. R.', 'format': u'(Audiobook CD)', 'path': u'/item/show/1905558093_the_hobbit', 'title': u'The Hobbit'}.

    """

    response = requests.get(BASE_URL+"/search", {'custom_query': u'title:{} author:{}'.format(title, author)})
    print response.url
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.content, "html.parser")
    results = process_response_to_records(soup)
    for result in results:
        if not result['author']:
            result['author'] = author

    return results

def process_response_to_records(soup):
    """Takes the catalog results, returns a list of dictionaries as described in search_all_records."""

    search_results = []
    top_info_divs = [div for div in soup.find_all('div') if 'class' in div.attrs and 'top_info' in div['class']]

    for data in top_info_divs:

        author_objects = [span for span in data.find_all('span') if 'author' in span.get('class', [])]
        if not author_objects:
            print "No author objects!"
            print data
            author = ""

        elif author_objects[0].a:
            author = author_objects[0].a.text.strip()
        else:
            author = author_objects[0].text.strip()

        title_obj = [span for span in data.find_all('span') if 'class' in span.attrs and 'title' in span['class']][0]
        title = title_obj.text.strip()
        path = title_obj.a['href']

        title_with_format = title_obj.a['title']
        if title_with_format:
            format_finder = re.search('\(.*\)', title_with_format)
            format = format_finder.group() # e.g. 'Fledgling (Audiobook CD)' --> 'Audiobook CD'
        else:
            print "Not written with format, searching further"
            secondary_info = [sib for sib in data.next_siblings if sib.name=="div" and "class" in sib.attrs and "secondary_info" in sib['class']][0]

            format_span = [span for span in secondary_info.find_all('span') if 'class' in span.attrs and 'format' in span['class']][0]
            format = format_span.text.strip()

        search_results.append({'title': title, 'author': author, 'format': format, 'path':path})

    return search_results



def check_type(record_soup):
    pass


def find_availability(title, author):
    pass

