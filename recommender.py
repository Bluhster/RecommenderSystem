# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, request, redirect, url_for
from flask_user import login_required, UserManager
import random

from models import db, User, Movie, MovieGenre, MovieTags
from read_data import check_and_read_data

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///movie_recommender.sqlite'  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning
    # Flask-User settings
    USER_APP_NAME = "Movie Recommender"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True  # Simplify register form

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db
db.init_app(app)  # initialize database
db.create_all()  # create database if necessary
user_manager = UserManager(app, db, User)  # initialize Flask-User management


@app.cli.command('initdb')
def initdb_command():
    global db
    """Creates the database tables."""
    check_and_read_data(db)
    print('Initialized the database.')

# The Home page is accessible to anyone
@app.route('/')
def home_page():
    # render home.html template

    return render_template("home.html")


# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/movies')
@login_required  # User must be authenticated
def movies_page():
    # String-based templates
    check_and_read_data(db)

    # first 10 movies
    # movies = Movie.query.limit(100).all()

    all_genres = ["Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", "Documentary", "Drama",
                  "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War",
                  "Western"]
    print("Movies Page")

    return render_template("filter_genre.html", all_genres=all_genres)

    # return render_template("movies.html", movies=movies)


@app.route('/filter_genre')
@login_required
def filter_genre():
    chosen_genre = request.args.to_dict()

    print("Received data:", chosen_genre)
    chosen_genre_list = list(chosen_genre.values())
    print(len(chosen_genre_list))
    movies = []
    if len(chosen_genre_list) > 0:
        print(chosen_genre_list)

        for idx, genre in enumerate(chosen_genre_list):
            movies = Movie.query \
                .filter(Movie.genres.any(MovieGenre.genre == genre)) \
                .filter(Movie.genres.any(MovieGenre.genre == 'Horror')) \
                .limit(10).all()
            print(movies)
    # all_genres = ["Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", "Documentary", "Drama", "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War", "Western"]
    return render_template("selected_genre.html", movies=movies)


@app.route('/selected_genre', methods=['GET'])
@login_required
def selected_genre():

    selected_genres = request.args.getlist('selectedGenres')
    print("Received data:", selected_genres)

    if selected_genres == 'No options selected.':
        movies = []
        # If no genres selected, show a random mix of 10 movies
        all_genres = ["Action", "Adventure", "Animation", "Children's", "Comedy", "Crime", "Documentary", "Drama",
                      "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War",
                      "Western"]
        random_genres = random.sample(all_genres, k=min(5, len(all_genres)))
        for genre in random_genres:
            genre_movies = Movie.query \
                .filter(Movie.genres.any(MovieGenre.genre == genre)) \
                .all()
            movies.extend(genre_movies)
        movies = random.sample(movies, k=min(10, len(movies)))

    else:
        # print("SELECTED GENRES", selected_genres)
        # Filter movies based on all selected genres
        movies = Movie.query
        for genre in selected_genres:
            movies = movies.filter(Movie.genres.any(MovieGenre.genre == genre))

        movies = movies.limit(15).all()

    return render_template("selected_genre.html", movies=movies)



# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
