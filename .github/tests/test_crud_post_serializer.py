
import pytest
from hypothesis import HealthCheck, given, settings, strategies as st
from hypothesis.extra.django import from_model
from django.contrib.auth.models import User
from main.models import Post
from main.serializers import PostSerializer
from rest_framework import serializers
from pytest_drf.util import url_for


@given(post=from_model(Post, user=from_model(User)))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.django_db
def test_serializer_fields(post):
    context = {'request': None}
    serializer = PostSerializer(post, context=context)
    data = serializer.data
    assert data['titulo'] == post.titulo
    assert data['cuerpo'] == post.cuerpo

@given(post=from_model(Post, user=from_model(User)))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.django_db
def test_serializer_hyperlinked(post):
    context = {'request': None}
    serializer = PostSerializer(post, context=context)
    assert issubclass(PostSerializer, serializers.HyperlinkedModelSerializer)
    assert PostSerializer.Meta.fields.__contains__('url') or serializer.fields.__contains__('url')
    assert serializer.data['url'] == url_for('post-detail', post.id)

@given(usuarios=st.lists(from_model(User), min_size=1, max_size=5))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow], max_examples=2)
@pytest.mark.django_db
def test_serializer_pk_related_field(post, usuarios):
    context = {'request': None}
    serializer = PostSerializer(post, context=context)
    data = serializer.data
    user_field = serializer.fields['user']
    assert isinstance(user_field, serializers.PrimaryKeyRelatedField)
    assert list(user_field.queryset) == list(User.objects.all())
    assert data['user'] == post.user.id
