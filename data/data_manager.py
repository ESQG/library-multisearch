import re
from datetime import datetime
import sys

from model import *
sys.path.append('../')
from server import app
from queries import use_sfpl, sfpl_locations

AVAILABILITY_QUERY = """
   SELECT c.call_number, c.total_available, bk.title, bk.author, b.branch_code, r.format_code
        FROM call_numbers AS c
        JOIN record_branch AS rb ON (rb.recbranch_id = c.record_id)
        JOIN records AS r ON (r.record_id = rb.record_id)
        JOIN branches AS b ON (b.branch_code = rb.branch_code)
        JOIN books AS bk ON (bk.book_id = r.book_id)
    WHERE bk.book_id = :book_id
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
            outfile.write("%s by %s") % (overlaps.title, overlaps.author)
            outfile.write('\n')
            for book in overlaps:
                outfile.write('\t')
                outfile.write(str(book))
                outfile.write('\n')


def add_book(title, author):
    already_there = Book.query.filter_by(title=title, author=author).first()

    if already_there:
        return already_there

    log_overlaps(title, author)     # In case of non-exact matches, write log

    book = Book(title=title, author=author)
    db.session.add(book)
    db.session.commit()
    return book


def get_stored_availability(book):

    book_results = []
    checked_out_formats = []

    db_pointer = db.session.execute(AVAILABILITY_QUERY, {'book_id':book.book_id})
    for row in db_pointer:
        call_number, total_available, title, author, branch_code, format_code = row  # Later: timestamp!
        available = bool(total_available)
        book_data = {'call_number': call_number,
                     'title': title,
                     'author': author,
                     'available': available,
                     'branch_code': branch_code,
                     'format': format_code,
                     'book_id': book.book_id
                     }
        if (not available) and (format_code not in checked_out_formats):
            checked_out_formats.append(format_code)
            book_results.append(book_data)
        elif available:
            book_results.append(book_data)

    return book_results


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

def update_availability(record):

    if record.format.digital:
        return

    current_availability = sfpl_locations.plain_results(record)
    current_availability.sort(key=lambda x: (x['status'] == 'CHECK SHELF'))
        # Put all CHECK SHELF statuses last

    tracking_branches = {}

    for result in current_availability:
        if result['branch'] in tracking_branches:
            branch, association = tracking_branches[result['branch']]

            association.total_copies += 1
            db.session.commit()

        else:
            write_log("Current result", str(result))
            branch = Branch.query.filter_by(name=result['branch']).one()

            association = RecordBranch.query.filter_by(branch_code=branch.branch_code, record_id=record.record_id).first()
            if not association:
                association = RecordBranch(branch_code=branch.branch_code, record_id=record.record_id, total_copies=1)
                db.session.add(association)
                db.session.commit()

            tracking_branches[branch.name] = [branch, association]
            association.total_copies = 1

        shelf = CallNumber.query.filter_by(record_id=association.recbranch_id, call_number=result['call_number']).first()
        if shelf:
            if shelf.total_available > 0 and result['status'] != 'CHECK SHELF':
                shelf.total_available = 0
            elif result['status'] == 'CHECK SHELF':
                shelf.total_available = 1   # Adjust later to library grouping
        else:
            shelf = CallNumber(record_id=association.recbranch_id, call_number=result['call_number'])
            db.session.add(shelf)
            if result['status'] == 'CHECK SHELF':
                shelf.total_available = 1
            else:
                shelf.total_available = 0   # Happens first, overwritten by available ones
        db.session.commit()

    return current_availability  # For convenience in interactive mode


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

