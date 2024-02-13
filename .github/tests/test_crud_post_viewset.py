
import pytest
from django.contrib.auth.models import User
from main.models import Post
from pytest_drf.util import url_for
from pytest_drf import AsUser
from pytest_lambda import lambda_fixture
from pytest_common_subject import precondition_fixture
from pytest_assert_utils import assert_model_attrs
from typing import Dict
from typing import Any, Dict
from urllib.parse import urlparse

from pytest_drf import (
    ViewSetTest,
    Returns200,
    Returns201,
    Returns204,
    Returns403,
    UsesGetMethod,
    UsesDeleteMethod,
    UsesDetailEndpoint,
    UsesListEndpoint,
    UsesPatchMethod,
    UsesPostMethod,
)

def express_post(post: Post, base) -> Dict[str, Any]:
    return {
        'cuerpo': post.cuerpo,
        'titulo': post.titulo,
        'url': base + url_for('post-detail',post.id),
        'user': post.user.id,
    }
    
def express_posts (posts, base) -> Dict[str, Any]:
    return [express_post(post, base) for post in posts]

@pytest.mark.django_db
class TestPostViewSet(ViewSetTest):
    list_url = lambda_fixture(
        lambda:
            url_for('post-list'))

    detail_url = lambda_fixture(
        lambda post:
            url_for('post-detail', post.pk))
    
    base_url = 'http://testserver'
    
    def check_structure(post, json):
        expected = express_post(post, TestPostViewSet.base_url)
        actual = json
        assert expected == actual
    
    
    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        posts = lambda_fixture(
            lambda user: [
                Post.objects.create(titulo=titulo, cuerpo=cuerpo, user=user)
                for titulo, cuerpo in [
                    ('Test Title', 'Test Body'),
                    ('Another Title', 'Another Body'),
                ]
            ],
            autouse=True,
        )
        
        def test_posts_list(self, posts, json):
            expected = express_posts(sorted(posts, key=lambda post: post.id),
                                     TestPostViewSet.base_url)
            actual = json
            assert expected == actual

    class TestCreateAdmin(
        UsesPostMethod,
        UsesListEndpoint,
        AsUser('admin_user'),
        Returns201,
    ):
        data = lambda_fixture(
            lambda admin_user: {
                'titulo': 'Test Create',
                'cuerpo': 'Cuerpo de mi test create',
                'user': admin_user.id,   
            }
        )
        
        initial_post_ids = precondition_fixture(
            lambda:
                set(Post.objects.values_list('id', flat=True)
            ), async_=False
        )
        
        def test_it_creates(self, initial_post_ids, json, data):
            # Recupera el id del post de la url devuelta por el serializador
            parsed_url = urlparse(json['url'])
            path_parts = parsed_url.path.strip('/').split('/')
            last_slug = path_parts[-1] if path_parts else None
            id=int(last_slug)
            
            #Comprueba la inserción de un único valor
            expected = initial_post_ids | {id}
            actual = set(Post.objects.values_list('id', flat=True))
            assert expected == actual
            
            #Comprueba los valores
            post = Post.objects.get(pk=id)
            # Modifica la estructura de los datos esperados para contener el user asociado
            data['user'] = User.objects.get(pk=data['user'])
            expected = data
            assert_model_attrs(post, expected)
            
            #Prueba la estructura del json
            TestPostViewSet.check_structure(post, json)
    
    class TestCreateUser(
        UsesPostMethod,
        UsesListEndpoint,
        AsUser('user'),
        Returns201,
    ):
        data = lambda_fixture(
            lambda user: {
                'titulo': 'Test Create',
                'cuerpo': 'Cuerpo de mi test create',
                'user': user.id,   
            }
        )
        
        initial_post_ids = precondition_fixture(
            lambda:
                set(Post.objects.values_list('id', flat=True)
            ), async_=False
        )
        
        def test_it_creates(self, initial_post_ids, json, data):
            # Recupera el id del post de la url devuelta por el serializador
            parsed_url = urlparse(json['url'])
            path_parts = parsed_url.path.strip('/').split('/')
            last_slug = path_parts[-1] if path_parts else None
            id=int(last_slug)
            
            #Comprueba la inserción de un único valor
            expected = initial_post_ids | {id}
            actual = set(Post.objects.values_list('id', flat=True))
            assert expected == actual
            
            #Comprueba los valores
            post = Post.objects.get(pk=id)
            # Modifica la estructura de los datos esperados para contener el user asociado
            data['user'] = User.objects.get(pk=data['user'])
            expected = data
            assert_model_attrs(post, expected)
            
            #Prueba la estructura del json
            TestPostViewSet.check_structure(post, json)

    class TestCreatePublicForbidden(
    UsesPostMethod,
    UsesListEndpoint,
    Returns403,
    ):
        pass
        
        
    class TestRetrievePublic(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
    ):
        def test_retrieve_structure(self, post, json):
            #Prueba la estructura del json
            TestPostViewSet.check_structure(post, json)

        
    class TestUpdateAdmin(
        UsesPatchMethod,
        UsesDetailEndpoint,
        AsUser('admin_user'),
        Returns200,
    ):
        data = lambda_fixture(
                lambda admin_user: {
                'titulo': 'Nuevo titulo',
                'cuerpo': 'Nuevo cuerpo',
                'user': admin_user.id
            }
        )
        
        def test_update_changes(self, data, post, json):
            # We must tell Django to grab fresh data from the database, or we'll
            # see our stale initial data and think our endpoint is broken!
            post.refresh_from_db()
            data['user'] = User.objects.get(pk=data['user'])
            expected = data
            assert_model_attrs(post, expected)
            
            #Prueba la estructura del json
            TestPostViewSet.check_structure(post, json)
            
    class TestUpdateOwner(
        UsesPatchMethod,
        UsesDetailEndpoint,
        AsUser('user'),
        Returns200,
    ):
        data = lambda_fixture(
                lambda user: {
                'titulo': 'Nuevo titulo',
                'cuerpo': 'Nuevo cuerpo',
                'user': user.id
            }
        )
        
        def test_update_changes(self, data, post, json):
            # We must tell Django to grab fresh data from the database, or we'll
            # see our stale initial data and think our endpoint is broken!
            post.refresh_from_db()
            data['user'] = User.objects.get(pk=data['user'])
            expected = data
            assert_model_attrs(post, expected)
            
            #Prueba la estructura del json
            TestPostViewSet.check_structure(post, json)

    class TestUpdatePublicForbidden(
    UsesPatchMethod,
    UsesDetailEndpoint,
    Returns403,
    ):
        pass
    
    class TestUpdateNoOwnerForbidden(
    UsesPatchMethod,
    UsesDetailEndpoint,
    AsUser('user2'),
    Returns403,
    ):
        pass

    class TestDestroyAdmin(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        AsUser('admin_user'),
        Returns204,
    ):
        initial_post_ids = precondition_fixture(
            lambda post:
                set(Post.objects.values_list('id', flat=True)
            ), async_=False
        )

        def test_it_deletes_post(self, initial_post_ids, post):
            expected = initial_post_ids - {post.id}
            actual = set(Post.objects.values_list('id', flat=True))
            assert expected == actual
    
    class TestDestroyOwner(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        AsUser('user'),
        Returns204,
    ):
        initial_post_ids = precondition_fixture(
            lambda post:
                set(Post.objects.values_list('id', flat=True)
            ), async_=False
        )

        def test_it_deletes_post(self, initial_post_ids, post):
            expected = initial_post_ids - {post.id}
            actual = set(Post.objects.values_list('id', flat=True))
            assert expected == actual
    
    class TestDestroyPublicForbidden(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        Returns403,
    ):
        pass

    class TestDestroyNoOwnerForbidden(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        AsUser('user2'),
        Returns403,
    ):
        pass
