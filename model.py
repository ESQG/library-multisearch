"""SQLAlchemy file for making tables in a database."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()



if __name__ == '__main__':

    from server import app
    connect_to_db(app)

    # Create our tables and some sample data
    db.create_all()
    example_data()

    print "Connected to DB."