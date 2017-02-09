"""SQLAlchemy file for making tables in a database."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Book(db.Model):

    __tablename__ = "books"

    book_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(100), nullable=False)

    author = db.Column(db.String(70), nullable=False)

    in_library = db.Column(db.Boolean, nullable=True)

# class OtherAuthor(db.Model):       # Make unique in PSQL!

#     __tablename__ = "other_authors"

#     row_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

#     book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))

#     name = db.Column(db.String(70), nullable=False)

#     book = db.relationship(Book, backref="other_authors")

class Record(db.Model):

    __tablename__ = "records"

    library_id = db.Column(db.Integer, primary_key=True, autoincrement=False)

    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))

    format = db.relationship('Format', secondary='RecordFormat')

    book = db.relationship('Book', backref="library_records")

class Copies(db.Model):

    __tablename__ = "copies"

    copy_id = db.Column(db.Integer, primary_key=True)

    library_id = db.Column(db.Integer, db.ForeignKey('records.library_id'))

    branch_code = db.Column(db.String(10), db.ForeignKey('branches.branch_code'))

    checked_out = db.Column(db.Integer, nullable=False)

    available = db.Column(db.Integer, nullable=False)

    book = db.relationship('Book', secondary='Record')

    branch = db.relationship('Branch', backref="copies")

    def __repr__(self):
        return "Copies(%s available, %s unavailable, %s)" % (self.available, self.checked_out, self.branch_code)


class Branch(db.Model):

    __tablename__ = "branches"

    branch_code = db.Column(db.String(10), primary_key=True)

    name = db.Column(db.String(25), nullable=False)

    longitude = db.Column(db.Numeric(8,5), nullable=True)

    latitude = db.Column(db.Numeric(8,5), nullable=True)

    address = db.Column(db.String(50), nullable=True)

    library_system = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return "Branch(%s, %s)" %(self.branch_code, self.name)


class User(db.Model):

    __tablename__ = "users"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    login = db.Column(db.String(30), nullable=False)

    password = db.Column(db.String(60), nullable=False)

    first_name = db.Column(db.String(25), nullable=True)

    last_name = db.Column(db.String(25), nullable=True)

    goodreads_id = db.Column(db.Integer, nullable=True)

    email = db.Column(db.String(65), nullable=False)

    books = db.relationship('Book', secondary='UserBook')


class UserBook(db.Model):

    __tablename__ = "user_books"

    row_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    book_id = db.Column(db.Integer, db.ForeignKey('books.book_id'))


class Format(db.Model):

    __tablename__ = "formats"

    format_code = db.Column(db.String(10), primary_key=True)

    name = db.Column(db.String(40))

    digital = db.Column(db.Boolean)

class RecordFormat(db.Model):

    row_id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    library_id = db.Column(db.Integer, db.ForeignKey('records.library_id'))

    format_code = db.Column(db.String(10), db.ForeignKey('formats.format_code'))

    record = db.relationship('Record')
    format = db.relationship('Format')

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///library_app'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


def example_data():
    pass

if __name__ == '__main__':

    from server import app
    connect_to_db(app)

    # Create our tables and some sample data
    db.create_all()
    example_data()

    # For running interactively
    print "Connected to DB %s" % app.config['SQLALCHEMY_DATABASE_URI']