import os
import random
import requests
from django.shortcuts import render
from dotenv import load_dotenv

load_dotenv()
OMDB_API_KEY = os.getenv("OMDB_API_KEY")

# Genres for random recommendation
GENRES = ["Romance", "Comedy", "Action", "Horror", "Animation", "Sci-Fi"]

# Number of movies per genre recommendation
MOVIES_PER_GENRE = 12

def movie_list_html(request):
    query = request.GET.get("q")
    top_rated_btn = request.GET.get("top_rated")
    genre_filter = request.GET.get("genre")
    page = int(request.GET.get("page", 1))  # pagination for Load More

    movies = []

    if query:
        # Search by user query
        url = f"http://www.omdbapi.com/?s={query}&page={page}&apikey={OMDB_API_KEY}"
        data = requests.get(url).json()
        movies = data.get("Search", [])

    elif top_rated_btn:
        # Dynamic top-rated using keyword search
        for p in range(1, 4):  # fetch first 3 pages
            url = f"http://www.omdbapi.com/?s=top rated&page={p}&apikey={OMDB_API_KEY}"
            data = requests.get(url).json()
            search_results = data.get("Search", [])
            if search_results:
                movies.extend(search_results)

    elif genre_filter:
        # Fetch multiple movies per genre
        for _ in range(MOVIES_PER_GENRE):
            url = f"http://www.omdbapi.com/?s={genre_filter}&page={random.randint(1, 10)}&apikey={OMDB_API_KEY}"
            data = requests.get(url).json()
            search_results = data.get("Search", [])
            if search_results:
                movies.append(random.choice(search_results))

    else:
        # Random recommendations per genre
        for genre in GENRES:
            for _ in range(MOVIES_PER_GENRE):
                search_query = random.choice([genre, "Movie", "Film"])
                url = f"http://www.omdbapi.com/?s={search_query}&page={random.randint(1, 10)}&apikey={OMDB_API_KEY}"
                data = requests.get(url).json()
                search_results = data.get("Search", [])
                if search_results:
                    movies.append(random.choice(search_results))

    return render(request, "movies/movie_list.html", {
        "movies": movies,
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
