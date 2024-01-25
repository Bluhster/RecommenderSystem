from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin

db = SQLAlchemy()

# Define the User data-model.
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

# table for the movies with all the information about each movie
class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    
    # reference other tables here for specific data
    genres = db.relationship('MovieGenre', backref='movie', lazy=True)
    tags = db.relationship('MovieTags', backref='movie', lazy=True)
    links = db.relationship('MovieLinks', backref='movie', lazy=True)
    ratings = db.relationship('MovieRatings', backref='movie', lazy=True)

# table for the movie genres
class MovieGenre(db.Model):
    __tablename__ = 'movie_genres'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    genre = db.Column(db.String(255), nullable=False, server_default='')

# table for the movie tags
class MovieTags(db.Model):
    __tablename__= 'movie_tags'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    tag = db.Column(db.String(255), nullable=False, server_default='')

# table for the links to imdb and tmdb
class MovieLinks(db.Model):
    __tablename__= 'movie_links'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    imdb = db.Column(db.String(255), nullable=False, server_default='')
    tmdb = db.Column(db.String(255), nullable=False, server_default='')

# table for the ratings
class MovieRatings(db.Model):
    __tablename__= 'movie_ratings'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)

# new table to fill with ratings given by registered users
class UserRatings(db.Model):
    __tablename__= 'user_ratings'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)