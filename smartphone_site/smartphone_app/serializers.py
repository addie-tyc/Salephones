from rest_framework import serializers
from smartphone_app.models import Ptt, Landtop


class LandtopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Landtop
        fields = ('title', 'storage', 'price')

class PttSerializer(serializers.ModelSerializer):

    old_price = serializers.FloatField()
    new_price = serializers.IntegerField()
    # landtop_id = serializers.IntegerField()

    class Meta:
        model = Ptt
        fields = ('id', 'title', 'storage', 'old_price', 'new_price')

class PttDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ptt
        fields = ('id', 'title', 'storage', 'price', 'link', 'box', 'source', 'created_at')

class PttGraphSerializer(serializers.ModelSerializer):

    old_price = serializers.FloatField()
    new_price = serializers.IntegerField()
    min_price = serializers.IntegerField()
    max_price = serializers.IntegerField()
    date = serializers.DateField()

    class Meta:
        model = Ptt
        fields = ('id', 'old_price', 'new_price', 'min_price', 'max_price', 'date', 'storage')

class ProfileSerializer(serializers.ModelSerializer):

   class Meta:
        model = Ptt
        fields = ('__all__')



