import requests
from bs4 import BeautifulSoup

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

    if 'branch' in location_td.text.lower():
        endpoint = location_td.text.lower().index('branch')    # fix for Main library
        location_name = location_td.text[:endpoint].strip()
    else:
        location_name = location_td.text

    for sib in location_td.next_siblings:
        if sib.name == 'td' and sib.get('data-label') == 'Call No':
            call_number = sib.text.strip()
        if sib.name == 'td' and sib.get('data-label') == 'Status':
            status = sib.text.strip()
            return (location_name, call_number, status)


def parse_branch_name(text):
    """E.g. "Portola Valley Branch (11)" becomes "Portola Valley" """
    pass


def find_availability_table(soup):
    heading_1s = soup.find_all('h1')
    for h1_element in heading_1s:
        if 'Available' in h1_element.text and 'not' not in h1_element.text.lower():            # fix with regular expressions!
            print h1_element.text
            return find_table_from_heading(h1_element)