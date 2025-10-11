from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class FavoriteMovie(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    movie_id = models.CharField(max_length=50)       # e.g. imdbID
    movie_title = models.CharField(max_length=255)
    poster_url = models.URLField(blank=True, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie_id')
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.movie_title} ({self.user})"
