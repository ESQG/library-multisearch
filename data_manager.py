def log_overlaps(title, author):

    search_author = author.split().strip(',')
    title_pieces = title.split()
    if title_pieces[0] == 'The' or title_pieces[0] == 'A' or title_pieces[0] == 'An':
        search_title = title_pieces[1]
    else:
        search_title = title_pieces[0]
    overlaps = Book.query.filter(Book.title.like('%' + search_title + '%'), Book.author.like('%' + search_author + '%'))

    if overlaps:
        with open('overlap-log.txt', 'a') as outfile:
            outfile.write(datetime.now().isoformat())
            outfile.write('\n')
            outfile.write("Found overlaps: ")
            outfile.write("%s by %s" % (title, author))
            outfile.write('\n')
            for book in overlaps:
                outfile.write('\t')
                outfile.write(str(book))
                outfile.write('\n')

def add_book(title, author):
    already_there = Book.query.filter_by(title=title, author=author).one()

    if already_there:
        return already_there

    log_overlaps(title, author)     # In case of non-exact matches, write log

    book = Book(title=title, author=author)
    db.session.add(book)
    db.session.commit()
    return book