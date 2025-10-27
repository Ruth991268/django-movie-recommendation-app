from django.urls import path
from . import views

urlpatterns = [
    path('html/', views.movie_list_html, name='movies-list-html'),
    path('html/<str:movie_id>/', views.movie_detail_html, name='movies-detail-html'),
    path('favorites/', views.favorite_list_view, name='movie-favorites'),
    path('favorite/toggle/', views.toggle_favorite_view, name='toggle-favorite'),
]