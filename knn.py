import pandas as pd
import sqlite3
import numpy as np
from sklearn.neighbors import NearestNeighbors
from scipy.spatial.distance import cosine
from sklearn.decomposition import TruncatedSVD

def recommend_movies(nr_recommendations = 5):
    # Load sqlite file
    conn = sqlite3.connect('instance/movie_recommender.sqlite')
    cursor = conn.cursor()

    # Fetch the names of all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    # Dictionary to hold each table as a dataframe
    dataframes = {}

    # Loop through the tables, read each table into a dataframe, and store it in the dictionary
    for table_name in tables:
        #print(table_name)
        table_name = table_name[0]
        query = f"SELECT * FROM {table_name}"
        dataframes[table_name] = pd.read_sql_query(query, conn)

    # Close the connection to the database
    conn.close()

    # # Print the dataframes
    # for table, df in dataframes.items():
    #     print(f"Table: {table}")
    #     print(df.head())  # This will print the first 5 rows of each dataframe

    movie_ratings = dataframes['movie_ratings']
    users = movie_ratings['user_id'].unique()
    movies = movie_ratings['movie_id'].unique()

    movies_df = pd.DataFrame(np.zeros((len(users), len(movies))))
    movies_df.index = users
    movies_df.columns = movies

    for user in users:
        indices = movie_ratings[movie_ratings['user_id']==user]['movie_id'].values
        ratings = movie_ratings[movie_ratings['user_id']==user]['rating'].values
        movies_df.loc[user, indices] = ratings

    movie_ratings_user = dataframes['user_ratings']
    users_user = movie_ratings_user['user_id'].unique()
    # movies_user = movie_ratings_user['movie_id'].unique()

    movies_df_user = pd.DataFrame(np.zeros((len(users_user), len(movies))))
    movies_df_user.index = users_user
    movies_df_user.columns = movies

    for user in users_user:
        indices = movie_ratings_user[movie_ratings_user['user_id']==user]['movie_id'].values
        ratings = movie_ratings_user[movie_ratings_user['user_id']==user]['rating'].values
        movies_df_user.loc[user, indices] = ratings

    # Knn using cosine similarity
    knn = NearestNeighbors(metric='cosine', algorithm='auto', n_neighbors=5, n_jobs=-1)
    knn.fit(movies_df)
    distances, indices = knn.kneighbors(movies_df_user, n_neighbors=5)
    #print(indices)

    # Assuming movie_ratings is your DataFrame, and indices is defined earlier
    filtered_ratings = movie_ratings[movie_ratings['user_id'] == indices[0][0]]
    # Now sort the filtered DataFrame by 'rating' column
    sorted_ratings = filtered_ratings.sort_values(by='rating', ascending=False)

    movies = dataframes['movies']

    # use multiple lists and for loops to filter out the nr_recommendations best rated movie_ids
    recommendations = []
    for i in range(nr_recommendations):
        recommendation = movies[movies.id==sorted_ratings.movie_id.values[i]]
        recommendations.append((recommendation.id.values, recommendation.title.values))
    
    recommended_ids = []
    for element in recommendations:
        recommended_ids.append(int(element[0][0]))    
    
    return recommended_ids



    # singular value decomposition with knn


    n_components = 344 # not sure if this is the best number --> See code below
    svd = TruncatedSVD(n_components=n_components)

    # Fit and transform the matrix
    movies_df_reduced = svd.fit_transform(movies_df)
    knn = NearestNeighbors(metric='cosine', algorithm='auto', n_neighbors=5, n_jobs=-1)
    knn.fit(movies_df_reduced)

    # Transform the new user's ratings using the same SVD object
    movies_df_user_reduced = svd.transform(movies_df_user)

    # Find the k-nearest neighbors
    distances, indices = knn.kneighbors(movies_df_user_reduced, n_neighbors=5)

    # We want to keep enough components to retain 90-95% of the variance (common approach).
    svd = TruncatedSVD(n_components=9724)  # A higher initial value
    svd.fit(movies_df)

    cumulative_variance = np.cumsum(svd.explained_variance_ratio_)
    n_components = np.argmax(cumulative_variance >= 0.95) + 1  # 95% variance explained

    print(f"Number of components to explain 95% variance: {n_components}")