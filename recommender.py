# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, request, flash, redirect, url_for, jsonify
from flask_user import login_required, UserManager
import random

from models import db, User, Movie, MovieGenre, MovieTags, UserRatings
from read_data import check_and_read_data
from flask_login import current_user
import json

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

    # first 10 movies
    movies = Movie.query.all()

    # only Romance movies
    #movies = Movie.query.filter(Movie.genres.any(MovieGenre.genre == 'Romance')).limit(10).all()

    # only Romance AND Horror movies
    # movies = Movie.query\
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Romance')) \
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Horror')) \
    #     .limit(10).all()

    return render_template("movies.html", movies=movies)


# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/filter_genre')
@login_required  # User must be authenticated
def filter_genre():
    # first 10 movies
    # movies = Movie.query.limit(100).all()

    all_genres = ["Action", "Adventure", "Animation", "Children", "Comedy", "Crime", "Documentary", "Drama",
                  "Fantasy", "Film-Noir", "Horror", "Musical", "Mystery", "Romance", "Sci-Fi", "Thriller", "War",
                  "Western"]
    print("Movies Page")

    return render_template("filter_genre.html", all_genres=all_genres)



@app.route('/selected_genre', methods=['GET', 'POST'])
@login_required
def selected_genre():
    if request.method == 'GET':
        # retrieve selected genres from previous view
        selected_genres = request.args.getlist('selectedGenres')
        print("Received data:", selected_genres)
        
        # if no genres were selected, just return 10 random movies to rate
        if len(selected_genres) == 0:
            all_movies = Movie.query.all()
            movies = random.sample(all_movies, k=10)

        else:
            # Filter movies based on all selected genres
            movies_query = Movie.query
            for genre in selected_genres:
                movies_query = Movie.query.filter(Movie.genres.any(MovieGenre.genre == genre))

            # Fetch the filtered movies from the query
            filtered_movies = movies_query.all()

            # Sample 10 movies from the filtered list
            movies = random.sample(filtered_movies, k=min(10, len(filtered_movies)))

        return render_template("selected_genre.html", movies=movies, genres=selected_genres)
    
    if request.method == 'POST':
        # small information block
        user_id = current_user.id
        ratings_data = request.form.getlist('ratings[]')
        selected_genres = request.form.getlist('genres')

        # if no genres were selected, just return 10 random movies to rate
        if len(selected_genres) == 0:
            all_movies = Movie.query.all()
            movies = random.sample(all_movies, k=10)

        else:
            # Filter movies based on all selected genres
            movies_query = Movie.query
            for genre in selected_genres:
                movies_query = Movie.query.filter(Movie.genres.any(MovieGenre.genre == genre))

            # Fetch the filtered movies from the query
            filtered_movies = movies_query.all()

            # Sample 10 movies from the filtered list
            movies = random.sample(filtered_movies, k=min(10, len(filtered_movies)))

        # Process the ratings
        for data in ratings_data:
            movie_id, rating = data.split(':')
            if rating != 'None':  # Filter out unrated movies
                rating = float(rating)
                new_rating = UserRatings(user_id=user_id, movie_id=movie_id, rating=rating)
                db.session.add(new_rating)
        db.session.commit()
        flash('Your ratings have been submitted!', 'success')

        if 'done_rating' in request.form:
            # If "I'm Done Rating" is clicked, redirect to a different page (e.g., home)
            return redirect(url_for('home_page'))

        return render_template("selected_genre.html", movies=movies, genres=selected_genres)

# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
