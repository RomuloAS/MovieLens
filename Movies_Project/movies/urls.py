from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("movies/", views.MovieListView.as_view(), name="movies"),
    path("movie/<int:movieId>", views.movie_detail, name="movie-detail"),
    path("movies/search/", views.get_movies_by_title, name="movies-form"),
    path("movies/genre/", views.movies_by_genre, name="movie-by-genre"),
]