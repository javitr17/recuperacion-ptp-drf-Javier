import pytest
from .utils import check_field
from django.db.models import BigAutoField, PositiveIntegerField, \
     TextField, ForeignKey, DateTimeField
from hypothesis import HealthCheck, given, settings
from hypothesis.extra.django import from_model
from main.models import Valoracion, Post
from django.contrib.auth.models import User

"""
Tests para Post
"""
def test_field_definition():
    check_field(clase=Valoracion, 
                name='id', 
                type=BigAutoField,
                pk=True)
    
    check_field(clase=Valoracion, 
                name='rating', 
                type=PositiveIntegerField,
                required=True)
    
    check_field(clase=Valoracion, 
                name='comment', 
                type=TextField,
                required=True)
    
    check_field(clase=Valoracion, 
                name='fecha_registro', 
                type=DateTimeField,
                required=True)
    
    check_field(clase=Valoracion, 
                name='user', 
                type=ForeignKey,
                fk_model=User,
                required=True)
    
    check_field(clase=Valoracion, 
                name='post', 
                type=ForeignKey,
                fk_model=Post,
                required=True)

def test_verbose_name_plural():
    assert Valoracion._meta.verbose_name_plural == 'Valoraciones'
    
@given(valoracion=from_model(Valoracion, user=from_model(User),
          post=from_model(Post, user=from_model(User))))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.django_db
def test_bd_impl(valoracion):
    assert True
    
@given(valoracion=from_model(Valoracion, user=from_model(User),
          post=from_model(Post, user=from_model(User))))
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture, HealthCheck.too_slow])
@pytest.mark.django_db
def test_str(valoracion):
    assert str(valoracion) == f'{str(valoracion.id)} - {valoracion.post.titulo} - {valoracion.user.username}'