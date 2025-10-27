from django.urls import path
from .views import ReviewListCreateView, ReviewDetailView, create_review_view

urlpatterns = [
    path('', ReviewListCreateView.as_view(), name='review-list'),
    path('<int:pk>/', ReviewDetailView.as_view(), name='review-detail'),
    path('review/create/', create_review_view, name='create-review'),
]
