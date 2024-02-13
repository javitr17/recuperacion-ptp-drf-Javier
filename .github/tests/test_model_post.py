import pytest
from .utils import check_field
from django.db.models import BigAutoField, CharField, TextField, ForeignKey
from hypothesis import HealthCheck, given, settings
from hypothesis.extra.django import from_model
from main.models import Post
from django.contrib.auth.models import User

"""
Tests para Post
"""
def test_field_definition():
    check_field(clase=Post, 
                name='id',
                type=BigAutoField,
                pk=True)
    
    check_field(clase=Post, 
                name='titulo', 
                type=CharField,
                max_length=100,
                required=True)
    
    check_field(clase=Post, 
                name='cuerpo', 
                type=TextField,
                help_text= "Incluye el contenido de tu articulo",
                required=True)
    
    check_field(clase=Post, 
                name='user', 
                type=ForeignKey,
                fk_model=User,
                required=True)

def test_verbose_name_plural():
    assert Post._meta.verbose_name_plural == 'Posts'

@given(post=from_model(Post, user=from_model(User)))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.django_db
def test_bd_impl(post):
    assert True
    
@given(post=from_model(Post, user=from_model(User)))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.django_db
def test_str(post):
    assert str(post) == f'{post.titulo} - {post.user.username}'

