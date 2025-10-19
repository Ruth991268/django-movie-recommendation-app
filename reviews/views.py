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
def movie_detail_view(request, imdb_id):
    api_key = os.environ.get('OMDB_API_KEY')
    if not api_key:
        return render(request, 'error.html', {'message': 'OMDB API key is not configured.'})

    # Fetch movie details from OMDB
    try:
        url = f'http://www.omdbapi.com/?i={imdb_id}&apikey={api_key}'
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        movie_data = response.json()
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError) as e:
        return render(request, 'error.html', {'message': f'Could not connect to the movie database: {e}'})

    # Find or create movie in local DB
    movie, created = Movie.objects.get_or_create(
        imdb_id=imdb_id,
        defaults={'title': movie_data.get('Title', 'N/A')}
    )

    if request.method == 'POST':
        rating = request.POST.get('rating')
        content = request.POST.get('content')

        if rating and content:
            Review.objects.create(
                user=request.user,
                movie=movie,
                rating=rating,
                content=content
            )
            return redirect('movies-detail-html', imdb_id=imdb_id)

    # Get all reviews for this movie
    reviews = Review.objects.filter(movie=movie).order_by('-created_at')
    context = {'movie': movie_data, 'reviews': reviews}
    return render(request, 'movies/movie_detail.html', context)


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

        if imdb_id and title and rating and content:
            movie, created = Movie.objects.get_or_create(
                imdb_id=imdb_id,
                defaults={'title': title}
            )
            Review.objects.create(
                user=request.user,
                movie=movie,
                rating=rating,
                content=content
            )
            return redirect('movies-list-html')

    context = {'search_query': search_query, 'search_results': search_results}
    return render(request, 'movies/create_review.html', context)
