"""SQLAlchemy file for making tables in a database."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):

    __tablename__ = "books"

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(200), nullable=False)

    author = db.Column(db.String(70), nullable=False)

    has_records = db.Column(db.Boolean, nullable=True)
    # True if SFPL has any copies of this book in any format, False if not.
    # This is deliberately denormalized, but should not need to be updated often.

    def __repr__(self):
        if len(self.title) > 100 and ":" in self.title:
            short_title = self.title.split(":")[0].strip()
        else:
            short_title = self.title
        return "Book(%s: %s by %s)" % (self.book_id, short_title, self.author)


class Record(db.Model):
    """A specific record for a book, held by a library using Bibliocommons.  Each record has
    one format; therefore a given book often has 4-5 records at SFPL or other libraries.
    A record usually refers to multiple copies of the book, which do not necessarily share the
    same call numbers, and which appear at different library branches; rather than track copies individually,
    the association table RecordBranch can be used to find how many copies of a book are at a given
    branch.
    it can be viewed by putting the bibliocommons_id into a URL, see examples below.

    Bibliocommons IDs seem to be shared across libraries, but the formats are not necessarily the same.
    For example, the bibliocommons_id of one record for "Fledgling" by Octavia Butler is 3123202093.
    https://seattle.bibliocommons.com/item/show/3123202093_fledgling is a physical book,
    as is https://brooklyn.bibliocommons.com/item/show/3123202093_fledgling, but
    https://sfpl.bibliocommons.com/item/show/3123202093_fledgling is an ebook.

    Therefore it may be useful to check bibliocommons_id numbers between different records referring
    to the same book, but in order to fix one format per record I won't use it as a primary key."""


    __tablename__ = "records"

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    bibliocommons_id = db.Column(db.BigInteger, nullable=False)

    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))

    format_code = db.Column(db.String(10), db.ForeignKey('formats.format_code'))

    # Relationships
    format = db.relationship('Format')
    book = db.relationship('Book', backref="library_records")

    def __repr__(self):
        return "Record(bibliocommons_id=%s, %s)" %(self.bibliocommons_id, self.format_code)

class RecordBranch(db.Model):

    __tablename__ = "record_branch"

    recbranch_id = db.Column(db.Integer, primary_key=True)

    record_id = db.Column(db.Integer, db.ForeignKey('records.record_id'))

    branch_code = db.Column(db.String(10), db.ForeignKey('branches.branch_code'))

    total_copies = db.Column(db.Integer, nullable=False)

    # total_available = db.Column(db.Integer, nullable=True)  # Moved to call number

    # Relationships
    record = db.relationship('Record')
    branch = db.relationship('Branch', backref='record_branch')

    def __repr__(self):
        return "Association(record %s with branch %s)" %(self.record_id, self.branch_code)

class CallNumber(db.Model):
    """A table used to list all the call numbers of a given RecordBranch entry.

    This is almost as specific as copies of a book, but multiple copies may share a call number."""

    __tablename__ = "call_numbers"

    callno_id = db.Column(db.Integer, primary_key=True)

    call_number = db.Column(db.String(30), nullable=False)

    recbranch_id = db.Column(db.Integer, db.ForeignKey('record_branch.recbranch_id'))

    total_available = db.Column(db.Integer, nullable=True)

    time_updated = db.Column(db.DateTime, nullable=True)

    # Relationship: used only for RecordBranch
    record_branch = db.relationship('RecordBranch', backref="call_numbers")

    def __repr__(self):
        if self.total_available is not None:
            return "CallNumber(%s for record %s, %s available)" %(self.call_number, self.record_id, self.total_available)
        else:
            return "CallNumber(%s for record %s, unknown available)" % (self.call_number, self.record_id)


class Branch(db.Model):

    __tablename__ = "branches"

    branch_code = db.Column(db.String(10), primary_key=True)

    name = db.Column(db.String(25), nullable=False)

    longitude = db.Column(db.Numeric(8,5), nullable=True)

    latitude = db.Column(db.Numeric(8,5), nullable=True)

    address = db.Column(db.String(50), nullable=True)

    library_code = db.Column(db.String(10), db.ForeignKey('libraries.library_code'))

    # Relationships: what libraries?
    library = db.relationship('LibrarySystem', backref="branches")

    def __repr__(self):
        return "Branch(%s, %s)" %(self.branch_code, self.name)

class LibrarySystem(db.Model):

    __tablename__ = "libraries"

    library_code = db.Column(db.String(10), primary_key=True)

    name = db.Column(db.String(50), nullable=False)


class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    email = db.Column(db.String(254), nullable=False)
    password = db.Column(db.String(60), nullable=False)

    first_name = db.Column(db.String(25), nullable=True)
    last_name = db.Column(db.String(25), nullable=True)

    #Relationships
    book_list = db.relationship('Book', secondary='user_books', backref="users")
    # branches = db.relationship('Branch', secondary='UserBranch', backref="users")


class GoodreadsUser(db.Model):
    """Some users will have Goodreads IDs; others may choose to enter their books directly.
    Therefore this class serves as an extension of the User table.
    It is also here in the hopes of implementing OAuth through Goodreads eventually."""

    __tablename__ = "goodreads_user"

    gruser_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    goodreads_id = db.Column(db.String(50), nullable=False, unique=True)

    #Relationship to User
    user = db.relationship('User', backref="goodreads")


# class PhoneUser later if using Twilio

class UserBook(db.Model):
    """An association table used to get a book list for each user."""

    __tablename__ = "user_books"

    userbook_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))

    # Relationships defined in User and Book classes


class UserBranch(db.Model):
    """Used to track which branches of the library a given user prefers."""

    __tablename__ = "user_branches"

    userbranch_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    branch_code = db.Column(db.String(10), db.ForeignKey('branches.branch_code'))



class Format(db.Model):

    __tablename__ = "formats"

    format_code = db.Column(db.String(10), primary_key=True)

    name = db.Column(db.String(40))

    digital = db.Column(db.Boolean)


def connect_to_db(app):
    """Connect a Flask app to our database."""

    # Configure to use our database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///library_app'
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.app = app
    db.init_app(app)
    print "I think I'm connected to the DB!"


def example_data():
    pass

if __name__ == '__main__':

    import sys
    sys.path.append('../')  # Allow imports from parent directory 
    from server import app
    connect_to_db(app)

    # Create our tables and some sample data
    db.create_all()
    example_data()

    # For running interactively
    print "Connected to DB %s" % app.config['SQLALCHEMY_DATABASE_URI']