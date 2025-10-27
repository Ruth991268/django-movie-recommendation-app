import os
import random
import requests
from django.shortcuts import render, redirect
from dotenv import load_dotenv
from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from reviews.models import Review, Movie
from .models import FavoriteMovie, FavoriteMovie

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

# Genres for random recommendation
GENRES = ["Romance", "Comedy", "Action", "Horror", "Animation", "Sci-Fi"]

# Number of movies per genre recommendation
MOVIES_PER_GENRE = 12

def fetch_from_omdb(params):
    """Helper function to fetch data from OMDB API with error handling."""
    base_url = "http://www.omdbapi.com/"
    params['apikey'] = OMDB_API_KEY
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        return response.json()
    except (requests.exceptions.RequestException, requests.exceptions.ConnectionError):
        # Return None or an empty dict if the request fails
        return None

def movie_list_html(request):
    query = request.GET.get("q")
    top_rated_btn = request.GET.get("top_rated")
    genre_filter = request.GET.get("genre")
    try:
        page = int(request.GET.get("page", 1))
    except ValueError:
        page = 1

    movies = []

    if query:
        # Search by user query
        params = {'s': query, 'page': page}
        data = fetch_from_omdb(params)
        if data:
            movies = data.get("Search", [])

    elif top_rated_btn:
        # Fetch a single page of top-rated movies to reduce API calls
        params = {'s': 'top rated', 'page': page}
        data = fetch_from_omdb(params)
        if data:
            movies = data.get("Search", [])

    elif genre_filter:
        # Fetch a single page for the selected genre
        params = {'s': genre_filter, 'page': page}
        data = fetch_from_omdb(params)
        if data:
            movies = data.get("Search", [])

    else:
        # Optimized: Fetch one random movie from each genre
        for genre in GENRES:
            params = {
                's': genre,
                'type': 'movie',
                'page': random.randint(1, 5) # Search within first 5 pages for variety
            }
            data = fetch_from_omdb(params)
            if data and data.get("Search"):
                movies.append(random.choice(data["Search"]))

    # Remove duplicates that might arise from random selections
    unique_movies_dict = {movie['imdbID']: movie for movie in movies}
    imdb_ids = list(unique_movies_dict.keys())

    # Fetch review statistics for the movies being displayed
    review_stats = Review.objects.filter(movie__imdb_id__in=imdb_ids).values('movie__imdb_id').annotate(
        average_rating=Avg('rating'),
        review_count=Count('id')
    )

    # Create a dictionary for easy lookup of review stats
    stats_map = {stat['movie__imdb_id']: stat for stat in review_stats}

    # Check which movies are in the user's favorites
    user_favorited_ids = set()
    if request.user.is_authenticated:
        user_favorited_ids = set(FavoriteMovie.objects.filter(
            user=request.user,
            movie_id__in=imdb_ids
        ).values_list('movie_id', flat=True))

    # Check which movies the current user has reviewed
    user_reviewed_ids = set()
    if request.user.is_authenticated:
        user_reviewed_ids = set(Review.objects.filter(
            user=request.user,
            movie__imdb_id__in=imdb_ids
        ).values_list('movie__imdb_id', flat=True))

    # Add review stats and favorite status to each movie
    for imdb_id, movie in unique_movies_dict.items():
        stats = stats_map.get(imdb_id)
        movie['average_rating'] = round(stats['average_rating'], 1) if stats else 0
        movie['review_count'] = stats['review_count'] if stats else 0
        movie['is_favorite'] = imdb_id in user_favorited_ids
        movie['user_has_reviewed'] = imdb_id in user_reviewed_ids
    
    return render(request, "movies/movie_list.html", {
        "movies": list(unique_movies_dict.values()),
        "genres": GENRES,
        "current_genre": genre_filter or "",
        "current_page": page
    })


def movie_detail_html(request, movie_id):
    """Fetches and displays detailed information for a single movie."""
    # Fetch movie details from OMDB
    movie_data = fetch_from_omdb({'i': movie_id, 'plot': 'full'})
    if not movie_data or movie_data.get('Response') == 'False':
        return render(request, '404.html', {'message': f"Movie with ID '{movie_id}' not found."}, status=404)

    # Find or create movie in local DB to associate reviews with
    movie, created = Movie.objects.get_or_create(
        imdb_id=movie_id,
        defaults={'title': movie_data.get('Title', 'N/A')}
    )

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        rating = request.POST.get('rating')
        content = request.POST.get('content')
        error_message = None

        try:
            rating_int = int(rating)
            if not 1 <= rating_int <= 10:
                raise ValueError("Rating must be between 1 and 10.")

            if content:
                Review.objects.create(user=request.user, movie=movie, rating=rating_int, content=content)
                return redirect('movies-detail-html', movie_id=movie_id)
        except (ValueError, TypeError):
            error_message = "Invalid rating. Please provide a number between 1 and 10."
        
        # Re-render page with error if submission fails
        reviews = Review.objects.filter(movie=movie).order_by('-created_at')
        context = {'movie': movie_data, 'reviews': reviews, 'error_message': error_message}
        return render(request, 'movies/movie_detail.html', context)

    reviews = Review.objects.filter(movie=movie).order_by('-created_at')
    return render(request, "movies/movie_detail.html", {"movie": movie_data, "reviews": reviews})


@login_required
def toggle_favorite_view(request):
    """Add or remove a movie from the user's favorites."""
    if request.method == 'POST':
        movie_id = request.POST.get('movie_id')
        movie_title = request.POST.get('movie_title')
        poster_url = request.POST.get('poster_url')

        favorite, created = FavoriteMovie.objects.get_or_create(
            user=request.user,
            movie_id=movie_id,
            defaults={'movie_title': movie_title, 'poster_url': poster_url}
        )

        if not created:
            # If the favorite already existed, delete it
            favorite.delete()

    return redirect(request.META.get('HTTP_REFERER', 'movies-list-html'))

@login_required
def favorite_list_view(request):
    favorites = FavoriteMovie.objects.filter(user=request.user)
    return render(request, 'movies/favorites.html', {'favorites': favorites})
