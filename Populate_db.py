import re
import argparse
import numpy as np
import pandas as pd
from tqdm import tqdm
from pymongo import MongoClient, ASCENDING

"""
Populate Mongo document database using 25M Movie
lens files.

The CSV files are filtered to be inserted into
the database.
"""

def getArguments():
    """Get arguments from terminal

    This function gets arguments from terminal via argparse

    Returns
    -------------
    arguments: Namespace
        Namespace object with all arguments
    """

    parser = argparse.ArgumentParser(
        description="Populate mongo Database\
                     with data from movie lens.")
    parser.add_argument("folder", type=str,
                   help="A folder with csv files.")
    
    return parser.parse_args()

def populate_database(folder, db):
    """Populate mongo database.

    This function uses pymongo to create a connection
    to mongo DB, parse the CSV files, and populate
    the database.

    Parameters
    -------------
    
    folder: str
        Path to the csv files.
    db: pymongo.database.Database
        A pymongo database connection object

    """

    # Read ratings.csv file
    print("Reading ratings")
    df_ratings = pd.read_table("{path}/ratings.csv".format(
                        path=folder), sep=",",
                        dtype = {"rating": float, "timestamp": int},
                        keep_default_na=False)
    # Groupby movieId
    columns = ["userId", "rating", "timestamp"]
    df_ratings["dict"] = df_ratings[columns].to_dict(orient="records")
    df_ratings = df_ratings.drop(columns=columns)
    df_ratings = df_ratings.groupby("movieId")["dict"].apply(list).to_dict()

    # Read tags.csv file
    print("Reading tags")
    df_tags = pd.read_table("{path}/tags.csv".format(
                        path=folder), sep=",",
                        dtype = {"tag": str, "timestamp": int},
                        keep_default_na=False)
    # Groupby movieId
    columns = ["userId", "tag", "timestamp"]
    df_tags["dict"] = df_tags[columns].to_dict(orient="records")
    df_tags = df_tags.drop(columns=columns)
    df_tags = df_tags.groupby("movieId")["dict"].apply(list).to_dict()

    # Read links.csv file
    print("Reading links")
    df_links = pd.read_table("{path}/links.csv".format(
                            path=folder), sep=",",
                            dtype = {"imdbId": str,"tmdbId": str},
                            keep_default_na=False)

    # Read movies.csv file
    print("Reading movies")
    df_movies = pd.read_table("{path}/movies.csv".format(
                        path=folder), sep=",",
                        keep_default_na=False)

    # Merge movies and links
    df_movies_links = pd.merge(df_movies, df_links, on="movieId")
    del df_movies
    del df_links

    # Read genome-scores.csv file
    print("Reading genome scores")
    df_genome_scores = pd.read_table(
                        "{path}/genome-scores.csv".format(
                        path=folder),
                        dtype = {"relevance": float}, sep=",",
                        keep_default_na=False)

    # Read genome-tags.csv file
    print("Reading genome tag")
    df_genome_tags = pd.read_table("{path}/genome-tags.csv".format(
                            path=folder),
                            sep=",", dtype = {"tag": str},
                            keep_default_na=False)

    # Merge genome tags and scores
    df_genome_tags_scores = pd.merge(df_genome_tags,
                                    df_genome_scores,
                                    on="tagId")
    del df_genome_tags
    del df_genome_scores
    # Groupby movieId
    columns = ["tagId", "tag", "relevance"]
    df_genome_tags_scores["dict"] = df_genome_tags_scores[
                                        columns].to_dict(orient="records")
    df_genome_tags_scores = df_genome_tags_scores.drop(columns=columns)
    df_genome_tags_scores = df_genome_tags_scores.groupby(
                                "movieId")["dict"].apply(list).to_dict()

    
    # Creating movies
    for index, row in tqdm(df_movies_links.iterrows(),
                desc="Creating movies"):
        movieId = row["movieId"]
        title = row["title"]
        imdbId = row["imdbId"]
        tmdbId = row["tmdbId"]

        # Extract year
        year = re.findall(r"\((\d{4})\)", row["title"])
        if year:
            year = year[-1]
            title = title.replace("({year})".format(
                    year=year), "").strip()
        else:
            year = 0
            title = title.strip()
        
        year = int(year)

        # Extract genres
        genres = row["genres"]
        genres = genres.split("|")

        if row["movieId"] in df_ratings:
            ratings = df_ratings[row["movieId"]]
        else:
            ratings = []

        if row["movieId"] in df_tags:
            tags = df_tags[row["movieId"]]
        else:
            tags = []

        if row["movieId"] in df_genome_tags_scores:
            genome_tags_scores = df_genome_tags_scores[row["movieId"]]
        else:
            genome_tags_scores = []

        movie = {
            "movieId": movieId,
            "title": title,
            "genres": genres,
            "year": year,
            "imdbId": imdbId,
            "tmdbId": tmdbId,
            "ratings": ratings,
            "tags": tags,
            "genome_tags": genome_tags_scores            
        }

        # Send to database
        db.movie.insert_one(movie)

if __name__ == '__main__':
    args = getArguments()
    folder = args.folder

    # Create Connection
    with MongoClient() as client:

        # Connect to Movies database
        db = client.Movies

        # Populate database
        populate_database(folder, db)

        # Create indexes
        db.movie.create_index("title")
        db.movie.create_index("movieId")
        db.movie.create_index("genres")
        db.movie.create_index("ratings.rating")
        db.movie.create_index([("genome_tags.tag", ASCENDING),
                            ("genome_tags.relevance", ASCENDING)])

        # Indexes information
        #db.movie.index_information()

        # Drop indexes
        # db.movie.drop_indexes()

        # Drop database
        # client.drop_database("Movies")