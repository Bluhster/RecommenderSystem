# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, request, flash, redirect, url_for
from flask_user import login_required, UserManager

from models import db, User, Movie, MovieGenre, MovieTags, MovieLinks, MovieRatings, UserRatings
from read_data import check_and_read_data
import random
from flask_login import current_user

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

@app.cli.command('test')
def test_command():
    global db
    # for loop to loop through all movies in movie table in database
    # collect and average all ratings for each movie 
    
    #movies = Movie.query.all()
    ratings = MovieRatings.query.all()
    averages_with_ids = [0]*(193609+1)
    temp_counts = [0]*(193609+1)
    #averages_with_movies = [0]*len(movies)

    for rating in ratings:
        averages_with_ids[rating.movie_id] += rating.rating
        temp_counts[rating.movie_id] += 1

    for i,count in enumerate(temp_counts):
        if count != 0:
            averages_with_ids[i] = averages_with_ids[i]/temp_counts[i]
        else:
            averages_with_ids[i] = None
    
    # for movie in movies:
    #     nr_of_ratings = MovieRatings.movie_id.count(movie.id)
    #     if nr_of_ratings != 0:
    #         averages_with_ids[movie.id] = averages_with_ids[movie.id]/nr_of_ratings
    print(averages_with_ids)

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
    movies = Movie.query.limit(100).all()

    # only Romance movies
    #movies = Movie.query.filter(Movie.genres.any(MovieGenre.genre == 'Romance')).limit(10).all()

    # only Romance AND Horror movies
    # movies = Movie.query\
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Romance')) \
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Horror')) \
    #     .limit(10).all()

    return render_template("movies.html", movies=movies)

@app.route('/rate_movies', methods=['GET', 'POST'])
@login_required
def rate_movies():
    if request.method == 'POST':
        user_id = current_user.id
        ratings_data = request.form.getlist('ratings[]')

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

        # If "Continue" is clicked, fetch new set of random movies
        movie_count = db.session.query(Movie).count()
        random_movies = Movie.query.offset(int(movie_count * random.random())).limit(5).all()
        return render_template("rate_movies.html", movies=random_movies)

    # Initial page load
    movie_count = db.session.query(Movie).count()
    random_movies = Movie.query.offset(int(movie_count * random.random())).limit(5).all()
    return render_template("rate_movies.html", movies=random_movies)


# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
