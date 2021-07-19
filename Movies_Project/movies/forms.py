from django import forms
from movies.models import Movie

class TitleForm(forms.Form):
    search_title = forms.CharField(label="Movie title", max_length=100)

class GenresForm(forms.Form):
    choices = [(genre, genre)
                    for genre in Movie.objects.distinct("genres")]
    genre_choose = forms.ChoiceField(choices=choices)