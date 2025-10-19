from django.contrib import admin

# Register your models here.
from .models import Review, Movie

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'imdb_id')
    search_fields = ('title', 'imdb_id')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'movie', 'rating', 'user', 'created_at')
    search_fields = ('movie__title', 'content', 'user__username')
    list_filter = ('rating', 'created_at')
