from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework. generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet

from .models import Film, Genre, Director
from .serializers import (
    FilmListSerializer,
    FilmDetailSerializer,
    FilmValidator,
    GenreSerializer,
    DirectorSerializer,
    DirectorListSerializer
)

class CustomPagination(PageNumberPagination):
    page_size = 3
    def get_paginated_response(self, data):
        return Response({
            'total': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })

class GenreListAPIView(ListCreateAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = CustomPagination

class GenreDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'id'

class DirectorViewSet(ModelViewSet):
    queryset = Director.objects.all()
    serializer_class = DirectorSerializer
    pagination_class = CustomPagination
    lookup_field = 'id'

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return DirectorListSerializer
        return self.serializer_class

@api_view(['GET', 'PUT', 'DELETE'])
def film_detail_api_view(request, id):
    try:
        film = Film.objects.get(id=id)
    except:
        return Response(data='Film not found!', status=status.HTTP_404_NOT_FOUND)
    if request.method == 'GET':
        data = FilmDetailSerializer(film, many=False).data
        return Response(data=data)
    elif request.method == 'DELETE':
        film.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    elif request.method == 'PUT':
        validator = FilmValidator(data=request.data)
        if not validator.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST,
                            data=validator.errors)
        validated = validator.validated_data

        film.title = validated.data['title']
        film.text = validated.data['text']
        film.release_date = validated.data['release_year']
        film.rating = validated.data['rating']
        film.is_hit = validated.data['is_hit']
        film.director_id = validated.data['director_id']
        film.genres.set(validated.data['genres'])
        film.save()
        return Response(status=status.HTTP_201_CREATED,
                        data=FilmDetailSerializer(film).data)

@api_view(['GET', 'POST'])
def film_list_create_api_view(request):
    if request.method == 'GET':
        films = Film.objects.select_related('director').prefetch_related('genres', 'reviews').all()
        list_ = FilmListSerializer(films, many=True).data
        return Response(data=list_)
    elif request.method == 'POST':
        validator = FilmValidator(data=request.data)
        if not validator.is_valid():
            return Response(status=HTTP_400_BAD_REQUEST,
                            data=validator.errors)
        validated = validator.validated_data

        title = validated.data['title']
        text = validated.data['text']
        release_date = validated.data['release_year']
        rating = validated.data['rating']
        is_hit = validated.data['is_hit']
        director_id = validated.data['director_id']
        genres = validated.data['genres']

        film = Film.objects.create(
            title=title,
            text=text,
            release_date=release_date,
            rating=rating,
            is_hit=is_hit,
            director_id=director_id
        )
        film.genres.set(genres)
        film.save()

        return Response(status=status.HTTP_201_CREATED,
                        data=FilmDetailSerializer(film).data)
