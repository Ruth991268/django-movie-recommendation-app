import os
import random
import requests
from django.shortcuts import render
from dotenv import load_dotenv
from django.db.models import Avg, Count
from reviews.models import Review

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
    page = int(request.GET.get("page", 1))  # pagination for Load More

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

    # Check which movies the current user has reviewed
    user_reviewed_ids = set()
    if request.user.is_authenticated:
        user_reviewed_ids = set(Review.objects.filter(
            user=request.user,
            movie__imdb_id__in=imdb_ids
        ).values_list('movie__imdb_id', flat=True))

    # Add review stats to each movie
    for imdb_id, movie in unique_movies_dict.items():
        stats = stats_map.get(imdb_id)
        movie['average_rating'] = round(stats['average_rating'], 1) if stats else 0
        movie['review_count'] = stats['review_count'] if stats else 0
        movie['user_has_reviewed'] = imdb_id in user_reviewed_ids
    
    return render(request, "movies/movie_list.html", {
        "movies": list(unique_movies_dict.values()),
        "genres": GENRES,
        "current_genre": genre_filter or "",
        "current_page": page
    })


def movie_detail_html(request, movie_id):
    url = f"http://www.omdbapi.com/?i={movie_id}&apikey={OMDB_API_KEY}&plot=full"
    data = requests.get(url).json()
    if data.get("Response") == "False":
        data = {"Title": "Not found", "Plot": "No data available", "imdbID": movie_id}
    return render(request, "movies/movie_detail.html", {"movie": data})
