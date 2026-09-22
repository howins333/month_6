from django.urls import path
from . import views
from .constants import retrieve_update_destroy, list_create

urlpatterns = [
    path('', views.film_list_create_api_view),
    path('<int:id>/', views.film_detail_api_view),
    path('genres/', views.GenreListAPIView.as_view()),
    path('genres/<int:id>/', views.GenreDetailAPIView.as_view()),
    path('directors/', views.DirectorViewSet.as_view(list_create)),
    path('directors/<int:id>/', views.DirectorViewSet.as_view(retrieve_update_destroy)),
]