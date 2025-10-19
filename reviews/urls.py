from django.urls import path
from .views import ReviewListCreateView, ReviewDetailView, movie_detail_view, create_review_view

urlpatterns = [
    path('', ReviewListCreateView.as_view(), name='review-list'),
    path('<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('movies/<str:imdb_id>/', movie_detail_view, name='movies-detail-html'),
    path('review/create/', create_review_view, name='create-review'),
]
