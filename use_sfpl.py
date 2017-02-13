import requests
from bs4 import BeautifulSoup
import sfpl_locations
import re

BASE_URL = "https://sfpl.bibliocommons.com"

example = BASE_URL + "/search?custom_query=" + "title%3AFledgling+author%3AOctavia+Butler"


# Bibliocommons recommends 'contributor' in its construction form, should I use that?
def search_all_records(title, author):
    """Returns a list of dictionaries, basically scraping together my own API from the library catalog.  Attributes I pull out
    are the title, author, and format as listed on the search results page, along with the local link to the actual record.

    Empty list if no records found; otherwise, each record should be formatted like so:
    {'author': u'Tolkien, J. R. R.', 'format': u'(Audiobook CD)', 'path': u'/item/show/1905558093_the_hobbit', 'title': u'The Hobbit'}.

    """

    search_results = []
    response = requests.get(BASE_URL+"/search", {'custom_query': 'title:{} author:{}'.format(title, author)})
    print response.url
    if response.status_code != 200:
        return search_results

    soup = BeautifulSoup(response.content, "html.parser")

    top_info_divs = [div for div in soup.find_all('div') if 'class' in div.attrs and 'top_info' in div['class']]

    for data in top_info_divs:

        author_objects = [span for span in data.find_all('span') if 'author' in span.get('class', [])]
        if not author_objects:
            print "No author objects!"
            print data

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
            # title = title.split('(')[0]     # e.g. 'Fledgling (Book)' --> Fledgling
        else:
            print "Not written with format, searching further"
            secondary_info = [sib for sib in data.next_siblings if sib.name=="div" and "class" in sib.attrs and "secondary_info" in sib['class']][0]

            format_span = [span for span in secondary_info.find_all('span') if 'class' in span.attrs and 'format' in span['class']][0]
            format = format_span.text.strip()

        search_results.append({'title': title, 'author': author, 'format': format, 'path':path})

    return search_results

    # titles = [span for span in soup.find_all('span') if 'class' in span.attrs and 'title' in span['class']]
    # # e.g. "<span class="title"><a href="/item/show/3123202093_fledgling" target="_parent" testid="bib_link" title="Fledgling - Novel (eBook)">Fledgling</a></span>"
    # # titles[1]['class'] returns [u'title']

    # for title in titles:
    #     data_to_return = {'title' : title}

    #     sibs = title.next_siblings
    #     for sib in sibs:
    #         if sib.name = 'span' and 'class' in sib.attrs and 'author' in sib['class']:
    #             author_pieces = sib.text.split()
    #             if 'By' == author_pieces[0]:
    #                 data_to_return['author'] = ' '.join(author_pieces[1:])
    #             else:
    #                 data_to_return['author'] = ' '.join(author_pieces)
    #                 log_issue(data_to_return)

    #     links.append(BASE_URL + title.a['href'])
    #     # For example above, title.a['href'] returns u'/item/show/3123202093_fledgling'

    # return links




def check_type(record_soup):
    pass


def find_availability(title, author):
    pass

