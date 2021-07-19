# Movie lens with mongodb and Django
---
***MongoDB document database was chosen to maximize the availability at the expense of consistency, as the data do not need to have a strong consistency and can have a more flexible schema.***

***ratings, tags, and genome tags were embedded in movie as the information could be retrieves in a single query when needed. There was no need to access any of them as an object on its own and joins/lookups were avoided. In addition, there are just a few hundreds of embedded documents, for this reason embedding was preferred. However, if more and more tags, genome tags, and ratings are to be included, then the database schema must be changed from embedding to referencing.***

### Simplified database schema
{

    "_id": "ObjectId('ObjectId')",
    "movieId": "id",
    "title": "title",
    "genres": ["genre1", "genre2", ...],
    "year": "year",
    "imdbId": "imdbId",
    "tmdbId": "tmdbId",
    "ratings": [
            {"userId": "id", "rating": "rating", "timestamp": timestamp}, ...
        ],
    "tags": [
            {"userId": "id", "tag": "tag", "timestamp": timestamp}, ...
        ],
    "genome_tags": [
            {"tagId": "id", "tag": "tag", "relevance": relevance}, ...
        ]

}

---
## Install, configure, and run the application

---

### Create environment with the dependencies
conda env create -f environment.yml

### Activate environment
conda activate Movie_Lens

### Create directory to save database
mkdir -p mongodb/data/db

### Run mongoDB
mongod --noauth --dbpath mongodb/data/db

### Run python Populate script

usage: Populate_db.py [-h] folder

>>Populate mongo Database with data from movie lens.
>>
>>positional arguments:
>>  folder      A folder with csv files.
>>
>>optional arguments:
>>  -h, --help  show this help message and exit

### Run server
python Movies_Project/manage.py runserver

---
