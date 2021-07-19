from mongoengine import Document, EmbeddedDocument, fields

class Rating(EmbeddedDocument):
    userId = fields.IntField()
    rating = fields.FloatField()
    timestamp = fields.IntField()

class Tag(EmbeddedDocument):
    userId = fields.IntField()
    tag = fields.StringField()
    timestamp = fields.IntField()

class Genome_Tag(EmbeddedDocument):
    tagId = fields.IntField()
    tag = fields.StringField()
    relevance = fields.FloatField()

class Movie(Document):
    movieId = fields.IntField()
    title = fields.StringField()
    genres = fields.ListField(fields.StringField())
    year = fields.IntField()
    imdbId = fields.StringField()
    tmdbId = fields.StringField()
    ratings = fields.EmbeddedDocumentListField(Rating)
    tags = fields.EmbeddedDocumentListField(Tag)
    genome_tags = fields.EmbeddedDocumentListField(Genome_Tag)

    def __str__(self):
        return self.title