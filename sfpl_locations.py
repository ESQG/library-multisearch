import requests
from bs4 import BeautifulSoup

BASE_URL = "https://sfpl.bibliocommons.com/item/show_circulation/"

def soupify(link):
    response = requests.get(link)
    if response.status_code == 200:
        raw_html = response.content
        return BeautifulSoup(raw_html, "html.parser")
    else:
        print "Cannot find %s" % link   # May want to make an error?
        return "Cannot find %s" % link

def find_heading_of_table(table_element):
    """Returns the most recent h1 heading above a given table.

    Input should be a BeautifulSoup element. For example:

    >>>type(table_element)
    <class 'bs4.element.Tag'>

    """

    for element in table_element.previous_elements:
        if element.name == 'h1':
            print element.text
            return element
        if element.name == 'table':
            print "Warning: found a table before a heading; returning table instead"
            return element

    print "No heading found for table starting with %s" % next(table_element.stripped_strings)


def find_table_from_heading(h1_element):
    """Returns the next table after an h1 element, using the BeautifulSoup methods."""

    for element in h1_element.next_elements:
        if element.name == 'table':
            return element
        # if element.name == 'h1':
        #     print "Warning: found another h1 before a table. Returning h1 instead"
        #     return element

    print "No table found for heading %s" % h1_element.text

def find_locations_in_table(table_element):
    locations = []

    for child in table_element.descendants:
        if child.name == 'td' and child.get('data-label') == 'Location':
            locations.append(find_call_no_and_status(child))
    return locations

def find_call_no_and_status(location_td):
    """Takes a location element of a table, and looks up the call number and status in the same row.

    Returns a tuple e.g. (u'Anaa', u'F ATWOOD M', u'CHECK SHELF')"""

    location_name = parse_branch_name(location_td.text)

    for sib in location_td.next_siblings:
        if sib.name == 'td' and sib.get('data-label') == 'Call No':
            call_number = sib.text.strip()
        if sib.name == 'td' and sib.get('data-label') == 'Status':
            status = sib.text.strip()
            return {'branch': location_name, 'call_number': call_number, 'status': status}


def parse_branch_name(text):
    """Takes 'Branch' out of the name of a library.

    >>> parse_branch_name(u'Main Library')
    u'Main Library'

    >>> parse_branch_name(u'Marina Branch')
    u'Marina'
    """

    if 'branch' in text.lower():
        endpoint = text.lower().index('branch')
        return text[:endpoint].strip()
    else:
        return text.strip()


def find_availability_table(soup):
    heading_1s = soup.find_all('h1')
    for h1_element in heading_1s:
        if 'Available' in h1_element.text and 'not' not in h1_element.text.lower():            # fix with regular expressions!
            print h1_element.text
            return find_table_from_heading(h1_element)

def all_availability(record):
    """Organizes all the availability information for a given record.

    If the library ID does not exist, this is a bug; the status code returned by Bibliocommons is 302, and the function returns False.

    One example: 

    {'available': [{'branch': u'Anza',
   'call_number': u'jF RHOD',
   'status': u'CHECK SHELF'},
  {'branch': u'Bayview', 'call_number': u'jF RHOD', 'status': u'CHECK SHELF'},
  {'branch': u'Main Library',
   'call_number': u'jF RHOD',
   'status': u'CHECK SHELF'},
  {'branch': u'Park', 'call_number': u'jF RHOD', 'status': u'CHECK SHELF'},
  {'branch': u'Richmond',
   'call_number': u'jF RHOD',
   'status': u'CHECK SHELF'}],
 'checked_out': [{'branch': u'Ocean View',
   'call_number': u'jF RHOD',
   'status': u'Due 02-11-17'},
  {'branch': u'West Portal',
   'call_number': u'jF RHOD',
   'status': u'ON HOLDSHELF'},
  {'branch': u'Western Addition',
   'call_number': u'jF RHOD',
   'status': u'Due 02-22-17'}]}
   """



    if record.format.digital:
        return [{'available': 'online'}]

    link = BASE_URL + str(record.bibliocommons_id)

    response = requests.get(link, allow_redirects=False)

    if response.status_code == 302:
        print "Status code 302: no record for id %s" % record.bibliocommons_id
        return False
    if response.status_code != 200:
        print "Error!", response.status_code
        return False

    soup = BeautifulSoup(response.content, "html.parser")
    results = {}

    tables = soup.find_all('table')

    for table in tables:
        header = find_heading_of_table(table)
        if 'Available' in header.text and 'not' not in header.text.lower():
            results['available'] = find_locations_in_table(table)
        elif 'Not available' in header.text:
            results['checked_out'] = find_locations_in_table(table)
        else:
            key = header.string.encode('utf-8')
            results[key] = find_locations_in_table(table)

    return results


def plain_results(record):
    """Like all_availability but less nested."""

    if record.format.digital:
        return [{'available': 'online'}]

    link = BASE_URL + str(record.bibliocommons_id)

    response = requests.get(link, allow_redirects=False)

    if response.status_code == 302:
        print "Status code 302: no record for id %s" % record.bibliocommons_id
        return False
    if response.status_code != 200:
        print "Error!", response.status_code
        return False

    soup = BeautifulSoup(response.content, "html.parser")
    results = []

    tables = soup.find_all('table')

    for table in tables:
        results.extend(find_locations_in_table(table))
    return results
