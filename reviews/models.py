from django.db import models
from django.contrib.auth.models import User

class Movie(models.Model):
    """
    Represents a movie stored in the local database.
    """
    imdb_id = models.CharField(max_length=20, unique=True, primary_key=True)
    title = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.title} ({self.imdb_id})"

class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='reviews', null=True)
    rating = models.IntegerField()
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)