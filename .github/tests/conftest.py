import pytest

from django.contrib.auth.models import User
from django.utils import timezone
from main.models import Post, Valoracion

from rest_framework.test import APIClient
from hypothesis import settings

settings.register_profile("my_profile", max_examples=15)
settings.load_profile("my_profile")

@pytest.fixture
def user():
    return User.objects.create_user(username='testuser', password='12345')

@pytest.fixture
def admin_user():
    return User.objects.create_superuser(username='admin', password='admin')

@pytest.fixture
def user2():
    return User.objects.create_user(username='testuser2', password='12345')

@pytest.fixture
def post(user):
    return Post.objects.create(titulo='Test Title', cuerpo='Test Body', user=user)

@pytest.fixture
def valoracion(user, post):
    return Valoracion.objects.create(rating=5, comment='Rating Comment', fecha_registro=timezone.now(), post=post, user=user)

@pytest.fixture
def client():
    return APIClient()