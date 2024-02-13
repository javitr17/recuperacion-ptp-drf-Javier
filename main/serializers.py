from rest_framework import serializers

from .models import Post, Valoracion
class PostSerializer(serializers.HyperlinkedModelSerializer):
    user=serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Post
        fields = ['url', 'id', 'titulo', 'cuerpo',
                  'user']

class ValoracionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Valoracion
        fields = '__all__'