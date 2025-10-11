from django.urls import path
from . import views

urlpatterns = [
    path('html/', views.movie_list_html, name='movies-html'),
    path('html/<str:movie_id>/', views.movie_detail_html, name='movies-detail-html'),
]
