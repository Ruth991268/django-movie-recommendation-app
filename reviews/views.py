import os
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from movies.views import fetch_from_omdb
from .models import Review, Movie
from .serializers import ReviewSerializer

from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly


# -------------------------
# DRF API Views
# -------------------------

class ReviewListCreateView(generics.ListCreateAPIView):
    queryset = Review.objects.all().order_by('-created_at')
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


# -------------------------
# Template-based Views
# -------------------------

@login_required
def create_review_view(request):
    search_query = request.GET.get('q', '')
    search_results = []

    if search_query:
        params = {'s': search_query, 'type': 'movie'}
        data = fetch_from_omdb(params)
        if data and data.get('Response') == 'True':
            search_results = data.get('Search', [])

    if request.method == 'POST':
        imdb_id = request.POST.get('imdb_id')
        title = request.POST.get('title')
        rating = request.POST.get('rating')
        content = request.POST.get('content')
        error_message = None

        if imdb_id and title and rating and content:
            try:
                rating_int = int(rating)
                if not 1 <= rating_int <= 10:
                    raise ValueError("Rating must be between 1 and 10.")
                
                movie, created = Movie.objects.get_or_create(
                    imdb_id=imdb_id,
                    defaults={'title': title}
                )
                Review.objects.create(
                    user=request.user, movie=movie, rating=rating_int, content=content
                )
                return redirect('movies-list-html')
            except (ValueError, TypeError):
                error_message = "Invalid rating. Please provide a number between 1 and 10."
                context = {'search_query': search_query, 'search_results': search_results, 'error_message': error_message}
                return render(request, 'movies/create_review.html', context)

    context = {'search_query': search_query, 'search_results': search_results}
    return render(request, 'movies/create_review.html', context)
