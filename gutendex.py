import os, math
from sqlalchemy import create_engine, or_, and_, func
from sqlalchemy import Column, String, Integer, Numeric, SmallInteger, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, backref
from paginator import pager

# Getting environment variable
HOST = os.environ['P_HOST']
PORT = os.environ['P_PORT']
DATABASE = os.environ['GUTENDEX']
USER = os.environ['P_USER']
PASSWORD = os.environ['P_PASSWORD']

# Connecting to database
db_string = 'postgresql://'+USER+':' + \
    PASSWORD + '@'+HOST+':'+PORT+'/'+DATABASE
db = create_engine(db_string)
base = declarative_base()
Session = sessionmaker(db)

base.metadata.create_all(db)

# Create schema of the database's table
# Mapping their relationship with each other

class Book(base):
    __tablename__ = 'books_book'

    id = Column(Integer, primary_key=True)
    download_count = Column(Integer)
    gutenberg_id = Column(Integer, unique=True, nullable=False)
    media_type = Column(String, nullable=False)
    title = Column(String)
    author = relationship('Book_Authors', backref='books_book', uselist=False)
    language = relationship(
        'Book_Languages', backref='books_book',  uselist=False)
    bookshelves = relationship('Book_Bookshelves', backref='books_book')
    subjects = relationship('Book_Subjects', backref='books_book')
    formats = relationship('Format', backref='books_book')


class Author(base):
    __tablename__ = 'books_author'

    id = Column(Integer, primary_key=True)
    birth_year = Column(SmallInteger)
    death_year = Column(SmallInteger)
    name = Column(String, nullable=False)


class Bookshelf(base):
    __tablename__ = 'books_bookshelf'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class Format(base):
    __tablename__ = 'books_format'
    
    id = Column(Integer, primary_key=True)
    mime_type = Column(String, nullable=False)
    url = Column(String, nullable=False)
    book_id = Column(Integer, ForeignKey('books_book.id'), nullable=False)


class Language(base):
    __tablename__ = 'books_language'
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, nullable=False)


class Subject(base):
    __tablename__ = 'books_subject'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Book_Authors(base):
    __tablename__ = 'books_book_authors'
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books_book.id'), nullable=False)
    author_id = Column(Integer, ForeignKey('books_author.id'), nullable=False)
    author = relationship(
        'Author', backref='books_book_authors', uselist=False)


class Book_Bookshelves(base):
    __tablename__ = 'books_book_bookshelves'
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books_book.id'), nullable=False)
    bookshelf_id = Column(Integer, ForeignKey(
        'books_bookshelf.id'), nullable=False)
    bookshelves = relationship('Bookshelf', backref='books_book_bookshelves')


class Book_Languages(base):
    __tablename__ = 'books_book_languages'
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books_book.id'), nullable=False)
    language_id = Column(Integer, ForeignKey(
        'books_language.id'), nullable=False)
    language = relationship('Language', backref='books_book_languages')


class Book_Subjects(base):
    __tablename__ = 'books_book_subjects'
    
    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books_book.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey(
        'books_subject.id'), nullable=False)
    subjects = relationship('Subject', backref='books_book_subjects')

# Handling the query
class Queries():
    
    def __init__(self):
        self.session = Session()
        self.per_page = 25
        
    def search_books(self,book_ids, languages, mime_types, authors, titles, topics, page):
        """
        Function to return the matched query to retrieve books
        """
        
        query = self.session.query(Book.id)

        books_to_return = []
        status = True

        # Filters with multiple criteria
        if book_ids:
            query = query.filter(Book.id.in_(book_ids))

        if languages:
            query = query.join(Book_Languages).join(
                Language).filter(Language.code.in_(languages))

        if mime_types:
            query = query.join(Format).filter(Format.mime_type.in_(mime_types))

        if authors:
            query = query.join(Book_Authors).join(
                Author).filter(or_(func.lower(Author.name).contains(author.lower()) for author in authors))

        if titles:
            query = query.filter(or_(func.lower(Book.title).contains(
                title.lower()) for title in titles))

        if topics:
            subject_ids = query.join(Book_Subjects).join(Subject).filter(
                or_(func.lower(Subject.name).contains(item.lower()) for item in topics)).all()
            bookshelf_ids = query.join(Book_Bookshelves).join(Bookshelf).filter(
                or_(func.lower(Bookshelf.name).contains(item.lower()) for item in topics)).all()
            books_to_return = list(set(subject_ids + bookshelf_ids))
        
        if not books_to_return:
            books_to_return = list(set(query.all()))

        result = self.session.query(Book).filter(Book.id.in_(
            books_to_return)).order_by(Book.download_count.desc())
        
        # Pagination
        try:
            paginated_results = pager(result, page, self.per_page)
        except:
            error = "That page contains no results"
            status = False
            return status, error

        total_result = len(books_to_return)
        page = paginated_results.page
        total_page = paginated_results.pages
        
        # Creating books object in required format
        output = []
        for book in paginated_results.items:
            one_book = {}
            bookshelves = []
            subjects = []
            download_links = {}

            for bookshelf in book.bookshelves:
                bookshelves.append(bookshelf.bookshelves.name)
            for subject in book.subjects:
                subjects.append(subject.subjects.name)
            for link in book.formats:
                download_links[link.mime_type] = link.url

            one_book['title'] = book.title
            if book.author:
                one_book['author'] = book.author.author.name
            else:
                one_book['author'] = None

            if book.language:
                one_book['language'] = book.language.language.code
            else:
                one_book['language'] = None

            one_book['bookshelves'] = bookshelves
            one_book['subjects'] = subjects

            one_book['download_links'] = download_links
            output.append(one_book)

        return status, [output, total_result, page, total_page]
