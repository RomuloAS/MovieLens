from django.http import HttpResponseRedirect
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views import generic
from django.http import Http404
from movies.models import Movie

from .forms import TitleForm, GenresForm

def index(request):
    """
    Initial page with number of movies
    and links.
    """

    # Count number of movies
    num_movies = Movie.objects.all().count()

    context = {
        "num_movies": num_movies
    }

    return render(request, "index.html", context=context)

class MovieListView(generic.ListView):
    """
    Get list with all movies using class
    """

    only_fields = ["movieId", "title", "year"]

    model = Movie
    template_name = "movies_list.html"
    context_object_name = "movies"
    queryset = Movie.objects.only(*only_fields)
    paginate_by = 15

def get_movies(request):
    """
    Get list with all movies using function
    """

    only_fields = ["movieId", "title", "year"]
    movies = Movie.objects.only(*only_fields)

    paginator = Paginator(movies, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "movies": movies,
        "page_obj": page_obj
    }

    return render(request, "movies_list.html", context=context)

def movie_detail(request, movieId):
    """
    Get movie details
    """

    try:
        pipeline = [
            {"$match" : {"movieId" : movieId}},
            {"$project": {"_id": 0, "movieId": 1,
                            "title": 1, "year": 1,
                            "genres": 1, "imdbId": 1,
                            "tmdbId": 1,
                            "rating_average": {"$avg": "$ratings.rating"},
                            "most_relevant_tag": {
                                "$arrayElemAt": [
                                    "$genome_tags.tag",
                                        {
                                            "$indexOfArray": [
                                            "$genome_tags.relevance",
                                            { "$max": "$genome_tags.relevance" }
                                            ]
                                        }
                                ]
                            }
                        }
            }
            ]


        movie = Movie.objects.aggregate(pipeline)
        movie = movie.next()
    except Movie.DoesNotExist:
        raise Http404("Movie does not exist")

    context = {
        "movie": movie
    }

    return render(request, "movie_detail.html", context=context)

def get_movies_by_title(request):
    """
    Get movies by title
    """

    if request.method == "POST":

        form = TitleForm(request.POST)
        search_title = form["search_title"].value()

        only_fields = ["movieId", "title", "year"]
        movies = Movie.objects(title__icontains=search_title).only(*only_fields)

    else:
        form = TitleForm()

    context = {
        "movies": movies
    }

    return render(request, "movies_list.html", context=context)

def movies_by_genre(request):
    """
    Movies top 10 by genre
    """

    form = GenresForm(request.POST)
    genre_choose = form["genre_choose"].value()

    genres = Movie.objects.distinct("genres")

    if genre_choose is None:
        genre = ""
    else:
        genre = genre_choose

    pipeline = [
            {"$match" : {"genres" : genre}},
            {"$project": {"_id": 0, "movieId": 1,
                            "title": 1, "year": 1,
                            "rating_average": {"$avg": "$ratings.rating"}
                        }
            },
            {"$sort": {"rating_average": -1}},
            {"$limit": 10}
            ]


    movies = Movie.objects.aggregate(pipeline)

    context = {
        "movies": movies,
        "genres": genres
    }

    return render(request, "movies_list.html", context=context)
