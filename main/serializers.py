from rest_framework import serializers
from .models import Post, Valoracion
from django.contrib.auth.models import User

class PostSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.PrimaryKeyRelatedField(many=False, queryset=User.objects.all())

    class Meta:
        model = Post
        fields = ['titulo','cuerpo','url','user']


class ValoracionSerializer(serializers.HyperlinkedModelSerializer):
    fecha_registro = serializers.ReadOnlyField()
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Valoracion
        fields = ['rating','fecha_registro','comment','url','post','user']
