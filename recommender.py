import csv
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_user import login_required, UserManager, UserMixin

class ConfigClass(object):
    SECRET_KEY = "This is an INSECURE secret!! DO NOT use this for production"

    SQLALCHEMY_DATABASE_URI = 'sqlite://movie_recommender.sqlite'   # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False #avoids SQLAlchemy warning

    USER_APP_NAME = "Movie Recommender" # Shown in and email templates and footers
    USER_ENABLE_EMAIL = False
    USER_ENABLE_USERNAME = True
    USER_REQUIRE_RETYPE_PASSWORD = True

app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')
app.app_context().push()

db = SQLAlchemy(app)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    #'NOCASE' is required to search case insentively when USER_IFIND_MODE is 'nocase_collation'
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

class Movie(db.Model):
    __talbename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.string(100, collation='NOCASE'), nullable=False, unique=True)
    genres = db.relationship('MovieGenre', backref='movie', lazy=True)

class MovieGenre(db.Model):
    __tablename__='movie_genres'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    genre = db.Column(db.String(255), nullable=False, server_default='')


def check_and_read_data(db):
    if Movie.query.count() == 0:
        with open('data/movies.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        id = row[0]
                        title = row[1]
                        movie = Movie(id=id, title=title)
                        db.session.add(movie)
                        genres = row[2].split('|')
                        for genre in genres:
                            movie_genre = MovieGenre(movie_id=id, genre=genre)
                            db.session.add(movie_genre)
                        db.session.commit() # save data to database
                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " movies read")

db.create_all()
check_and_read_data(db)

user_manager = UserManager(app, db, User)

@app.route('/')
def home_page():
    return render_template("home.html")

@app.route('/movies')
@login_required # user must be authenticated
def movies_page():
    # first 10 movies (limit response to 10)
    movies = Movie.query.limit(10).all()

    # only Romance movies
    # movies = Movie.query.filter(Movie.genres.any(MovieGenre.genre == 'Romance')).limit(10).all()

    # only Romance AND Horror movies
    # movies = Movie.query\
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Romance')) \
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Horror')) \
    #     .limit(10).all()
    
    return render_template("movies.html", movies = movies)

if __name__ == '__main__':
    app.run(port=5000, debug=True)