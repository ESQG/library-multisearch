This repository is for a "library MultiSearch" app, which is my project developed at Hackbright Academy during February 2017.

Currently I am working on a "minimum viable product": an app that can intake my Goodreads to-read list, and when I choose a branch of the San Francisco Public library, my app will display which of the books are available at that branch right now.  (I'll count downloadable digital products as their own branch.)

Please do not make pull requests to this repository as all the code needs to be mine.  However if you have run across this project and would like to contribute "user flow" suggestions, I would be happy to hear them.

In addition to the Python packages in requirements.txt, if you would like to reproduce this project, you will need to install PostgreSQL.

Current useful examples:  Run the example_locations() function from example_urls.py to see how a book's information is looked up.  Run the my_toread_list() function from use_goodreads.py to see how a list of books can be found from a to-read shelf.