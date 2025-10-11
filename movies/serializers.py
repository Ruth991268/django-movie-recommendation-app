from rest_framework import serializers

class MovieListSerializer(serializers.Serializer):
    Title = serializers.CharField()
    Year = serializers.CharField()
    imdbID = serializers.CharField()
    Type = serializers.CharField()
    Poster = serializers.CharField()


class MovieDetailSerializer(serializers.Serializer):
    Title = serializers.CharField()
    Year = serializers.CharField(required=False)
    Rated = serializers.CharField(required=False, allow_blank=True)
    Released = serializers.CharField(required=False, allow_blank=True)
    Runtime = serializers.CharField(required=False, allow_blank=True)
    Genre = serializers.CharField(required=False, allow_blank=True)
    Director = serializers.CharField(required=False, allow_blank=True)
    Writer = serializers.CharField(required=False, allow_blank=True)
    Actors = serializers.CharField(required=False, allow_blank=True)
    Plot = serializers.CharField(required=False, allow_blank=True)
    Language = serializers.CharField(required=False, allow_blank=True)
    Poster = serializers.CharField(required=False, allow_blank=True)
