"""SQLAlchemy file for making tables in a database."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///library_app'
    app.config['SQLALCHEMY_ECHO'] = True
    db.app = app
    db.init_app(app)


if __name__ == '__main__':

    from server import app
    connect_to_db(app)

    # Create our tables and some sample data
    db.create_all()
    example_data()

    # For running interactively
    print "Connected to DB %s" % app.config['SQLALCHEMY_DATABASE_URI']