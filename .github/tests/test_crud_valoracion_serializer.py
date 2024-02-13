
from attr import field
import pytest
from hypothesis import HealthCheck, given, settings, strategies as st
from hypothesis.extra.django import from_model
from django.contrib.auth.models import User
from main.models import Valoracion, Post
from main.serializers import ValoracionSerializer
from rest_framework import serializers
from pytest_drf.util import url_for
from .utils import get_field


@pytest.mark.django_db
def test_serializer_commom_fields(valoracion):
    context = {'request': None}
    serializer = ValoracionSerializer(valoracion, context=context)
    data = serializer.data
    assert data['rating'] == valoracion.rating
    assert data['fecha_registro'] == valoracion.fecha_registro
    assert data['comment'] == valoracion.comment
    # assert data['post'] == url_for('post-detail', valoracion.post.id)
    # assert data['user'] == valoracion.user.id


@pytest.mark.django_db
def test_serializer_hyperlinks(valoracion):
    context = {'request': None}
    serializer = ValoracionSerializer(valoracion, context=context)
    data = serializer.data
    
    assert issubclass(ValoracionSerializer, serializers.HyperlinkedModelSerializer)
    
    assert ValoracionSerializer.Meta.fields.__contains__('url') or serializer.fields.__contains__('url')
    assert serializer.data['url'] == url_for('valoracion-detail', valoracion.id)

    
    assert ValoracionSerializer.Meta.fields.__contains__('post') or serializer.fields.__contains__('post')
    assert serializer.data['post'] == url_for('post-detail', valoracion.post.id)


@pytest.mark.django_db
def test_serializer_pk_related_field(valoracion):
    context = {'request': None}
    serializer = ValoracionSerializer(valoracion, context=context)
    data = serializer.data
    user_field = serializer.fields['user']
    assert isinstance(user_field, serializers.PrimaryKeyRelatedField), f"Esperado: PrimaryKeyRelatedField, Obtenido: {type(user_field)}"
    assert user_field.read_only == True, "El campo user debería ser de solo lectura"
    assert data['user'] == valoracion.user.id
