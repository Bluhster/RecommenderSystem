import csv
from sqlalchemy.exc import IntegrityError
from models import Movie, MovieGenre, MovieTags, MovieLinks, MovieRatings

def check_and_read_data(db):
    # check if we have movies in the database
    # read data if database is empty
    if Movie.query.count() == 0:
        # read movies from csv
        with open('data/movies.csv', newline='', encoding='utf8') as movies:
            movies = csv.reader(movies, delimiter=',')
            count = 0
            for mov_row in movies:
                if count > 0:
                    try:
                        id = mov_row[0]
                        title = mov_row[1]
                        movie = Movie(id=id, title=title)
                        db.session.add(movie)
                        genres = mov_row[2].split('|')  # genres is a list of genres
                        for genre in genres:  # add each genre to the movie_genre table
                            movie_genre = MovieGenre(movie_id=id, genre=genre)
                            db.session.add(movie_genre)
                        db.session.commit()  # save data to database
                    
                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " movies read")

        # read tags from csv
        with open('data/tags.csv', newline='', encoding='utf8') as tags:
            tags = csv.reader(tags, delimiter=',')
            count = 0
            for tag_row in tags:
                if count > 0:
                    try:
                        mov_id = tag_row[1]
                        mov_tag = MovieTags(movie_id=mov_id, tag=tag_row[2])
                        db.session.add(mov_tag)
                        db.session.commit()  # save data to database
                    
                    except IntegrityError:
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " movie tags added")
        
        # read links from csv
        with open('data/links.csv', newline='', encoding='utf8') as links:
             links = csv.reader(links, delimiter=',')
             count = 0
             for link_row in links:
                if count > 0:
                    try:
                        mov_id2 = link_row[0]
                        imdb =  "https://www.imdb.com/title/tt" + link_row[1] + "/"
                        tmdb = "https://www.themoviedb.org/movie/" + link_row[2]
                        movie_links = MovieLinks(movie_id=mov_id2, imdb=imdb, tmdb=tmdb)
                        db.session.add(movie_links)
                        db.session.commit()
                    
                    except IntegrityError:
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " links added")
        
        # read ratings from csv
        with open('data/ratings.csv', newline='', encoding='utf8') as ratings:
            ratings = csv.reader(ratings, delimiter=',')
            count = 0
            for ratings_row in ratings:
                if count > 0:
                    try:
                        mov_id3 = ratings_row[1]
                        userid = ratings_row[0]
                        rating = ratings_row[2]
                        movie_rating = MovieRatings(movie_id=mov_id3, user_id=userid, rating=rating)
                        db.session.add(movie_rating)
                        db.session.commit()
                    
                    except IntegrityError:
                        db.session.rollback()
                        pass
                count += 1
                if count % 1000 == 0:
                    print(count, " ratings added")