import re  # title parsing, mostly
from datetime import datetime, timedelta  # timestamps for logging and checking last updated
import sys   # to append path for parent imports
from decimal import Decimal   # to process PostgreSQL numeric types returned as decimals

# Import error for exception!
from sqlalchemy.orm.exc import NoResultFound

# Local import
from model import *

# Import from sibling directories
sys.path.append('../')
from queries import use_sfpl, sfpl_locations


AVAILABILITY_QUERY = """
   SELECT c.call_number, c.total_available, bk.title, bk.author, 
   b.branch_code, r.format_code, c.time_updated
        FROM call_numbers AS c
        JOIN record_branch AS rb ON (rb.recbranch_id = c.recbranch_id)
        JOIN records AS r ON (r.record_id = rb.record_id)
        JOIN branches AS b ON (b.branch_code = rb.branch_code)
        JOIN books AS bk ON (bk.book_id = r.book_id)
    WHERE bk.book_id = :book_id
    ;
    """

USER_AVAILABLE_QUERY = """
   SELECT c.call_number, c.total_available, bk.book_id, bk.title, bk.author, 
   b.branch_code, r.format_code, c.time_updated
        FROM call_numbers AS c
        JOIN record_branch AS rb ON (rb.recbranch_id = c.recbranch_id)
        JOIN records AS r ON (r.record_id = rb.record_id)
        JOIN branches AS b ON (b.branch_code = rb.branch_code)
        JOIN books AS bk ON (bk.book_id = r.book_id)
    WHERE bk.book_id IN (SELECT book_id FROM user_books 
        WHERE user_id = :user_id
        )
    ;
"""

def log_overlaps(title, author):

    search_author = author.split()[0].strip(',')
    title_pieces = title.split()
    if title_pieces[0] == 'The' or title_pieces[0] == 'A' or title_pieces[0] == 'An':
        search_title = title_pieces[1]
    else:
        search_title = title_pieces[0]
    overlaps = Book.query.filter(Book.title.like('%' + search_title + '%'), Book.author.like('%' + search_author + '%')).all()

    if overlaps:
        with open('overlaps.log', 'a') as outfile:
            outfile.write(datetime.now().isoformat())
            outfile.write('\n')
            outfile.write("Found possible overlaps: ")
            outfile.write("%s by %s" % (title, author))
            outfile.write(" and ")
            for book in overlaps:
                outfile.write('\t')
                outfile.write(str(book))
                outfile.write('\n')


def add_book(title, author):
    title = re.sub(r'\(.*\)', '', title).strip()    # Improves library search results
    already_there = Book.query.filter_by(title=title, author=author).first()

    if already_there:
        return already_there

    log_overlaps(title, author)     # In case of non-exact matches, write log

    book = Book(title=title, author=author)
    db.session.add(book)
    db.session.commit()
    return book


def get_book(book_id):
    return Book.query.get(book_id)


def get_books(book_id_list):
    return Book.query.filter(Book.book_id.in_(book_id_list)).all()


def stored_availability_for_user(user_id):

    book_results = []
    checked_out_formats = []
    db_pointer = db.session.execute(USER_AVAILABLE_QUERY, {'user_id': user_id})
    for row in db_pointer:
            call_number = row[0]
            available = bool(row[1])
            book_id = row[2]
            title = row[3]
            author = row[4]
            branch_code = row[5]
            format_code = row[6]
            time_updated = row[7]
            
            book_data = {'call_number': call_number,
                         'title': title,
                         'author': author,
                         'available': available,
                         'branch_code': branch_code,
                         'format': format_code,
                         'book_id': book_id,
                         'time_updated': time_updated
                         }
            if (not available) and (format_code not in checked_out_formats):
                checked_out_formats.append(format_code)
                book_results.append(book_data)
            elif available:
                book_results.append(book_data)

    available_formats = {data['format'] for data in book_results if data['available']}
    for data in book_results:
        if (not data['available']) and (data['format'] in available_formats):
            book_results.remove(data)

    return book_results


def get_stored_availability(book_id):

    book_results = []
    checked_out_formats = []

    db_pointer = db.session.execute(AVAILABILITY_QUERY, {'book_id': book_id})
    for row in db_pointer:
        call_number, total_available, title, author, branch_code, format_code, time_updated = row  # Later: timestamp!
        available = bool(total_available)
        book_data = {'call_number': call_number,
                     'title': title,
                     'author': author,
                     'available': available,
                     'branch_code': branch_code,
                     'format': format_code,
                     'book_id': book_id,
                     'time_updated': time_updated
                     }
        if (not available) and (format_code not in checked_out_formats):
            checked_out_formats.append(format_code)
            book_results.append(book_data)
        elif available:
            book_results.append(book_data)

    available_formats = {data['format'] for data in book_results if data['available']}
    for data in book_results:
        if (not data['available']) and (data['format'] in available_formats):
            book_results.remove(data)

    return book_results


def branch_dict_list(library_system="sfpl"):
    """Print condensed dictionary of branches."""
    branches = Branch.query.all()
    branches_info = []

    for branch in branches:
        table_attrs = {key: value for key, value in vars(branch).items() if "_" != key[0] and value != library_system}
        if table_attrs['latitude'] and table_attrs['longitude']:
            table_attrs['latitude'] = float(table_attrs['latitude'])
            table_attrs['longitude'] = float(table_attrs['longitude'])
        branches_info.append(table_attrs)

    return branches_info

def records_from_book(book):
    
    record_data = use_sfpl.search_all_records(book.title, book.author)
    desired_records = []

    for data in record_data:
        if check_matching_title(book, data['title']) and check_matching_author(book, data['author']):

            bibliocommons_id_finder = re.search(r'\d{9,11}', data['path'])
            if bibliocommons_id_finder:
                bibliocommons_id = bibliocommons_id_finder.group()
            else:
                write_log("No id found in path", str(data)) #Error will be raised by SQLAlchemy

        format_code = codify_format(data['format'])

        if format_code and bibliocommons_id:
            old_record = Record.query.filter_by(bibliocommons_id=bibliocommons_id, book_id=book.book_id).first()
            if not old_record:
                record = Record(book_id=book.book_id, bibliocommons_id=bibliocommons_id, format_code=format_code)
                db.session.add(record)
                db.session.commit()
            else:
                record = old_record

            desired_records.append(record)

        else:
            write_log("Bad search result", str(book), str(data))

    return desired_records


def get_recent_stored_availability(book):
    time_stamp = datetime.now()
    records = get_stored_availability(book.book_id)
    recent_records = []

    for record in records:
        if record['time_updated'] is not None:
            time_elapsed = (time_stamp - record['time_updated']).seconds
            if time_elapsed < 2000:
                recent_records.append(record)


def update_availability(record):

    if record.format.digital:
        return

    current_availability = sfpl_locations.plain_results(record)
    current_availability.sort(key=lambda x: (x['status'] == 'CHECK SHELF'))
        # Put all CHECK SHELF statuses last
    time_stamp = datetime.now()
    tracking_branches = {}

    for result in current_availability:
        result['branch'] = re.sub(r'\(\d+\)', '', result['branch']).strip()

        if result['branch'] in tracking_branches:
            branch, association = tracking_branches[result['branch']]

            association.total_copies += 1
            db.session.commit()

        else:
            # write_log("Current result", str(result))
            try:
                branch = Branch.query.filter_by(name=result['branch']).one()
            except NoResultFound:
                write_log("Branch not found", result['branch'])
                continue

            association = RecordBranch.query.filter_by(branch_code=branch.branch_code, record_id=record.record_id).first()
            if not association:
                association = RecordBranch(branch_code=branch.branch_code, record_id=record.record_id, total_copies=1)
                db.session.add(association)
                db.session.commit()

            tracking_branches[branch.name] = [branch, association]
            association.total_copies = 1

        shelf = CallNumber.query.filter_by(recbranch_id=association.recbranch_id, call_number=result['call_number']).first()
        if shelf:
            shelf.time_updated = time_stamp
            if shelf.total_available > 0 and result['status'] != 'CHECK SHELF':
                shelf.total_available = 0
            elif result['status'] == 'CHECK SHELF':
                shelf.total_available = 1   # Adjust later to library grouping
        else:
            shelf = CallNumber(recbranch_id=association.recbranch_id, call_number=result['call_number'])
            shelf.time_updated = time_stamp
            db.session.add(shelf)
            if result['status'] == 'CHECK SHELF':
                shelf.total_available = 1
            else:
                shelf.total_available = 0   # Happens first, overwritten by available ones
        db.session.commit()

    return current_availability  # For convenience in interactive mode


def new_user(user_info):
    """Inputs a new user to the database, after checking that the email provided is not already in use.
    Returns None if the email is already taken; otherwise, returns the assigned user_id."""

    if len(user_info['email']) not in range(3, 255):
        return None

    email_used = User.query.filter_by(email=user_info['email']).first()
    if email_used:
        return "Email used"

    password = user_info['password'][:60]
    first_name = user_info['first-name'] or None
    last_name = user_info['last-name'] or None
    new_user = User(email=user_info['email'], password=user_info['password'], 
                    first_name=first_name, last_name=last_name)
    db.session.add(new_user)
    db.session.commit()
    return new_user.user_id


def update_user_booklist(book_ids, user_id):
    """Given a user ID and list of book IDs, update the database to reflect that."""
    
    stored_book_ids = set(get_user_book_ids(user_id))

    for book_id in stored_book_ids:
        if book_id not in stored_book_ids:
            new_assoc = UserBook(book_id=book_id, user_id=user_id)
            db.session.add(new_assoc)
    db.session.commit()


def get_user_book_ids(user_id):
    """Given a user ID, return a list of book IDs associated with that user."""

    associations = UserBook.query.filter_by(user_id=user_id).all()
    return [assoc.book_id for assoc in associations]


def get_user_by_email(user_info):
    """For use by the server: look up a uer by email."""

    email = user_info['email']
    user = User.query.filter_by(email=email).first()
    if not user:
        return

    password = user_info['password'][:60]
    if password != user.password:
        return "Wrong password"
    
    return user.user_id


def check_matching_title(book, title):
    """Check if a title is correct.  Need to be careful about this!"""

    return True


def check_matching_author(book, author):
    """Check if an author is correct.  Need to be careful about this!"""

    return True


def codify_format(format_string):
    """Returns None if format is non-standard."""

    format_string = format_string.strip('()').strip()
    if format_string == 'eBook':
        return 'ebook'
    elif format_string == 'Book':
        return 'book'
    elif format_string == 'Large Print' or format_string == 'LP':
        return 'large'
    elif 'Audiobook' in format_string:
        if 'CD' in format_string:
            return 'audiocd'
        elif 'Downloadable' in format_string:
            return 'eaudio'
        elif 'hoopla' in format_string.lower():
            return 'hoopla'
    elif 'DVD' in format_string:
        pass
    else:
        write_log("New format found", format_string)



def write_log(message, *args):
    with open("data_manager.log", 'a') as log_file:
        log_file.write('\n')
        log_file.write(datetime.now().isoformat())
        log_file.write('\t')
        log_file.write(message + ":")
        log_file.write('\t')
        log_file.write('\n'.join(args))


if __name__ == '__main__':
    connect_to_db(app)
    from server import app
