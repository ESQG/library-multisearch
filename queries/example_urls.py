import requests
from bs4 import BeautifulSoup

# Local imports
import sfpl_locations


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




def example_locations():
    soup = sfpl_locations.soupify(availability[2])
    table = sfpl_locations.find_availability_table(soup)
    return sfpl_locations.find_locations_in_table(table)
