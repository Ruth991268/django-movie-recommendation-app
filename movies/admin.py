from django.contrib import admin
from .models import FavoriteMovie

@admin.register(FavoriteMovie)
class FavoriteMovieAdmin(admin.ModelAdmin):
    list_display = ('movie_title', 'movie_id', 'user', 'date_added')
    search_fields = ('movie_title', 'movie_id', 'user__username')
