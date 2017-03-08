Library List

This is a web app (i.e. a dynamic website) that allows a user to provide a list of books by title and author, then searches the San Francisco Public Library for all the user's books.  This can be used by providing a Goodreads bookshelf link directly, or by signing up for an account, adding books by title and author or from a Goodreads bookshelf.  All books are stored in the database, and their availability updated if it is a day out of date; however, signing up for an account will make it easeir to manage a booklist. 

Back end:

A Python server, using the Flask web framework and Jinja2 templates to render HTML pages.  All permanent info, except for a JSON file of library addresses, is stored in a PostgreSQL database.

Front end:

HTML rendered by the back end, styled with Bootstrap, a CSS file in static/styles.css.

The background image stored in /static/LibraryImage.jpg has not been added to Github, but it can be found at https://unsplash.com/photos/lIWF2uHxs0Q .

Javascript with JQuery; makes AJAX calls.

APIs and other web interfacing:

The front end uses the Googlemaps (Javascript) API to embed a clickable map of all 28 branches of SFPL.  

On the back end, the web API and scraping code is found in the queries/ folder.  The Goodreads API is used to get booklists; for the library pages, the Bibliocommons API is not accessible to the general public, so these pages are scraped.

Requirements before running server.py:

pip install requirements.txt to configure Python
Install PostgreSQL, and create a database called library_app (or change the name in model.py), as well as a test database called testdb.  

Run the seed.py file in the data folder.

Register for a Goodreads API, and store the resulting API key and secret in your environment variables, as GOODREADS_API_KEY and GOODREADS_API_SECRET respectively.

Register for a Googlemaps Geocode API key, and a Googlemaps Javascript API key; store those as well.  (I used the former to get latitudes and longitudes of library branches by address, and store them in the database; so it is not necessary.  The latter is for embedding a map, and needs to be exported to the environment as GOOGLEMAPS_API_KEY).