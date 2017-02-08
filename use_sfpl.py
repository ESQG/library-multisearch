import requests
from bs4 import BeautifulSoup
import sfpl_locations

BASE_URL = "https://sfpl.bibliocommons.com"

example = BASE_URL + "/search?custom_query=" + "title%3AFledgling+author%3AOctavia+Butler"


# Bibliocommons recommends 'contributor' in its construction form, should I use that?
def search_all_records(title, author):
    """Need to use urllib to encode"""

    links = []
    response = requests.get(BASE_URL+"/search", {'custom_query': 'title:{} author:{}'.format(title, author)})
    print response.url
    if response.status_code != 200:
        return links

    soup = BeautifulSoup(response.content, "html.parser")

    titles = [span for span in soup.find_all('span') if 'class' in span.attrs and 'title' in span['class']]
    # e.g. "<span class="title"><a href="/item/show/3123202093_fledgling" target="_parent" testid="bib_link" title="Fledgling - Novel (eBook)">Fledgling</a></span>"
    # titles[1]['class'] returns [u'title']

    for title in titles:
        links.append(BASE_URL + title.a['href'])
        # For example above, title.a['href'] returns u'/item/show/3123202093_fledgling'

    return links

def check_type(record_soup):
    pass


def find_availability(title, author):
    pass

