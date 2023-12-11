import csv
from sqlalchemy.exc import IntegrityError
from models import Movie, MovieGenre, MovieTags, MovieLinks#, MovieRatings

def check_and_read_data(db):
    # check if we have movies in the database
    # read data if database is empty
    print("check and read data was called")
    if Movie.query.count() == 0:
        # read movies from csv
        with open('data/movies.csv', newline='', encoding='utf8') as movies:
            with open('data/tags.csv', newline='', encoding='utf8') as tags:
                with open('data/links.csv', newline='', encoding='utf8') as links:
                    with open('data/ratings.csv', newline='', encoding='utf8') as ratings:
                        mov_reader = csv.reader(movies, delimiter=',')
                        tag_reader = csv.reader(tags, delimiter=',')
                        link_reader = csv.reader(links, delimiter=',')
                        rating_reader = csv.reader(ratings, delimiter=',')

                        count = 0
                        for mov_row, tag_row, link_row, rating_row in zip(mov_reader, tag_reader, link_reader, rating_reader):
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

                                    mov_id = tag_row[1]
                                    mov_tag = MovieTags(movie_id=mov_id, tag=tag_row[2])
                                    db.session.add(mov_tag)

                                    mov_id2 = link_row[0]
                                    imdb =  "https://www.imdb.com/title/tt" + link_row[1] + "/"
                                    tmdb = "https://www.themoviedb.org/movie/" + link_row[2]
                                    movie_links = MovieLinks(movie_id=mov_id2, imdb=imdb, tmdb=tmdb)
                                    db.session.add(movie_links)

                                    db.session.commit()  # save data to database
                                except IntegrityError:
                                    print("Ignoring duplicate movie: " + title)
                                    db.session.rollback()
                                    pass
                            count += 1
                            if count % 100 == 0:
                                print(count, " movies read")

        # # read movies from csv
        # with open('data/tags.csv', newline='', encoding='utf8') as csvfile:
        #     reader = csv.reader(csvfile, delimiter=',')
        #     count = 0
        #     for row in reader:
        #         if count > 0:
        #             try:
        #                 user_id = row[0]
        #                 movie_id = row[1]
        #                 timestamp = row[3]
        #                 movie_tag = MovieTags(movie_id=movie_id, tag=row[2])
        #                 db.session.add(movie_tag)
        #                 db.session.commit()  # save data to database
        #             except IntegrityError:
        #                 #print("Ignoring duplicate movie: ")
        #                 db.session.rollback()
        #                 pass
        #         count += 1
        #         if count % 100 == 0:
        #             print(count, " movies read")


