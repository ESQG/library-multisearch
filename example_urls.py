import requests
from bs4 import BeautifulSoup

catalog_entry = ["https://sfpl.bibliocommons.com/item/show/1024641093_the_handmaids_tale",
"https://sfpl.bibliocommons.com/item/show/2294407093_fledgling",
"https://sfpl.bibliocommons.com/item/show/2294407093",
"https://sfpl.bibliocommons.com/item/show/1970540093_fledgling",
"https://sfpl.bibliocommons.com/item/show/3018942093_fledgling",
]


availability = ["https://sfpl.bibliocommons.com/item/show_circulation/1024641093_the_handmaids_tale", 
"https://sfpl.bibliocommons.com/item/show_circulation/1024641093",
"https://sfpl.bibliocommons.com/item/show_circulation/1970540093",
"https://sfpl.bibliocommons.com/item/show_circulation/2294407093",
"https://sfpl.bibliocommons.com/item/show_circulation/3018942093_fledgling"
]


search_query = ["https://sfpl.bibliocommons.com/search?custom_query=(contributor%3A(Octavia+Butler)+AND+title%3A(Fledgling))",
]

def soupify(link):
    response = requests.get(link)
    if response.status_code == 200:
        raw_html = response.content
        return BeautifulSoup(raw_html, "html.parser")
    else:
        print "Cannot find %s" % link   # May want to make an error?
        return None

def find_heading_of_table(table_element):
    for element in table_element.previous_elements:
        if element.name == 'h1':
            print element.text
            return element

def find_locations_of_table(table_element):
    pass