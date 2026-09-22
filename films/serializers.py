from rest_framework import serializers
from .models import Film, Director, Genre
from rest_framework.exceptions import ValidationError

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'

class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = 'id first_name last_name birthday'.split()

class DirectorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = 'id first_name last_name'.split()


class FilmDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Film
        fields = '__all__'

class FilmListSerializer(serializers.ModelSerializer):
    director = DirectorSerializer()
    # genres = GenreSerializer(many=True)
    genres = serializers.SerializerMethodField()


    class Meta:
        model = Film
        # fields = [ 'id', 'title', 'rating', 'created_at']
        # fields = '__all__'
        # exclude = ['text', 'updated']
        fields = 'id title rating created_at director genres reviews'.split()
        # depth = 1
    def get_genres(self, film):
        return film.genre_list()

class FilmValidator(serializers.Serializer):
    title = serializers.CharField(max_length=255, min_length=1)
    text = serializers.CharField(required=False, default='No text')
    release_date = serializers.IntegerField()
    rating = serializers.FloatField(min_value=1, max_value=10)
    is_hit = serializers.BooleanField(default=False)
    director_id = serializers.IntegerField()
    genres = serializers.ListField(child=serializers.IntegerField())

    def validate_director_id(self, director_id):
        director_id = director_id['director_id']
        try:
            Director.objects.get(id=director_id)
        except Director.DoesNotExist:
            raise ValidationError('Director does not exist')

        return director_id

    def validate_genres(self, genres):
        genres_from_db = Genre.objects.filter(id__in=genres)
        if len(genres_from_db) != len(genres):
            raise ValidationError('Genre does not exist')
        return genres

