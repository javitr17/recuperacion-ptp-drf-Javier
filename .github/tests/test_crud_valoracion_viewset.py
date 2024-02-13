
import pytest
from main.models import Valoracion
from pytest_drf.util import url_for
from pytest_drf import AsUser, APIViewTest
from pytest_lambda import lambda_fixture
from pytest_common_subject import precondition_fixture
from pytest_assert_utils import assert_model_attrs
from typing import Dict
from typing import Any
from urllib.parse import urlparse
from django.utils import timezone
import random
from lorem_text import lorem


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

def express_valoracion(valoracion: Valoracion, base) -> Dict[str, Any]:
    return {
        'rating': valoracion.rating,
        'fecha_registro': valoracion.fecha_registro.isoformat().replace('+00:00', 'Z'),
        'url': base + url_for('valoracion-detail',valoracion.id),
        'comment': valoracion.comment,
        'user': valoracion.user.id,
        'post': base + url_for('post-detail',valoracion.post.id),
    }
    
def express_valoraciones (posts, base) -> Dict[str, Any]:
    return [express_valoracion(post, base) for post in posts]

@pytest.mark.django_db
class TestValoracionViewSet(ViewSetTest):
    list_url = lambda_fixture(
        lambda:
            url_for('valoracion-list'))

    detail_url = lambda_fixture(
        lambda valoracion:
            url_for('valoracion-detail', valoracion.pk))
    
    base_url = 'http://testserver'
    
    def check_structure(post, json):
        expected = express_valoracion(post, TestValoracionViewSet.base_url)
        actual = json
        assert expected == actual
    
    
    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
    ):
        valoraciones = lambda_fixture(
            lambda user, post: [
                Valoracion.objects.create(rating=rating, comment=comment,
                                          fecha_registro=timezone.now(), 
                                          post=post, user=user)
                for rating, comment in [
                    (1, 'Comment asd'),
                    (2, 'Comment   asdf asdfasd'),
                    (5, 'Comment   asdf asdfasd'),
                    (4, 'Comment   f asdfasd'),
                    (3, 'Comment   asdf assd'),
                ]
            ],
            autouse=True,
        )
        
        def test_valoraciones_list(self, valoraciones, json):
            expected = express_valoraciones(sorted(valoraciones, key=lambda valoracion: valoracion.id),
                                     TestValoracionViewSet.base_url)
            actual = json
            assert expected == actual

    class TestCreateAdmin(
        UsesPostMethod,
        UsesListEndpoint,
        AsUser('admin_user'),
        Returns201,
    ):
        data = lambda_fixture(
            lambda post: {
                'rating': random.randint(1, 5),
                'comment': lorem.sentence(),
                'post': TestValoracionViewSet.base_url 
                    + url_for('post-detail', post.id),   
            }
        )
        
        initial_valoraciones_ids = precondition_fixture(
            lambda:
                set(Valoracion.objects.values_list('id', flat=True)
            ), async_=False
        )
        
        def test_it_creates(self, initial_valoraciones_ids, json, data, admin_user):
            # Recupera el id del post de la url devuelta por el serializador
            parsed_url = urlparse(json['url'])
            path_parts = parsed_url.path.strip('/').split('/')
            last_slug = path_parts[-1] if path_parts else None
            id=int(last_slug)
            
            #Comprueba la inserción de un único valor
            expected = initial_valoraciones_ids | {id}
            actual = set(Valoracion.objects.values_list('id', flat=True))
            assert expected == actual
            
            #Comprueba los valores
            valoracion = Valoracion.objects.get(pk=id)
            # Modifica la estructura de los datos esperados para contener el user asociado
            data['user'] = admin_user
            data['post'] = valoracion.post
            expected = data
            assert_model_attrs(valoracion, expected)
            
            #Prueba la estructura del json
            TestValoracionViewSet.check_structure(valoracion, json)
    
    class TestCreateUser(
        UsesPostMethod,
        UsesListEndpoint,
        AsUser('user'),
        Returns201,
    ):
        data = lambda_fixture(
            lambda post: {
                'rating': random.randint(1, 5),
                'comment': lorem.sentence(),
                'post': TestValoracionViewSet.base_url 
                    + url_for('post-detail', post.id),   
            }
        )
        
        initial_valoraciones_ids = precondition_fixture(
            lambda:
                set(Valoracion.objects.values_list('id', flat=True)
            ), async_=False
        )
        
        def test_it_creates(self, initial_valoraciones_ids, json, data, user):
            # Recupera el id del post de la url devuelta por el serializador
            parsed_url = urlparse(json['url'])
            path_parts = parsed_url.path.strip('/').split('/')
            last_slug = path_parts[-1] if path_parts else None
            id=int(last_slug)
            
            #Comprueba la inserción de un único valor
            expected = initial_valoraciones_ids | {id}
            actual = set(Valoracion.objects.values_list('id', flat=True))
            assert expected == actual
            
            #Comprueba los valores
            valoracion = Valoracion.objects.get(pk=id)
            # Modifica la estructura de los datos esperados para contener el user asociado
            data['user'] = user
            data['post'] = valoracion.post
            expected = data
            assert_model_attrs(valoracion, expected)
            
            #Prueba la estructura del json
            TestValoracionViewSet.check_structure(valoracion, json)

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
        def test_retrieve_structure(self, valoracion, json):
            #Prueba la estructura del json
            TestValoracionViewSet.check_structure(valoracion, json)

        
    class TestUpdateAdmin(
        UsesPatchMethod,
        UsesDetailEndpoint,
        AsUser('admin_user'),
        Returns200,
    ):
        data = lambda_fixture(
            lambda post: {
                'rating': random.randint(1, 5),
                'comment': lorem.sentence(),
                'post': TestValoracionViewSet.base_url 
                    + url_for('post-detail', post.id),   
            }
        )
        
        def test_update_changes(self, data, valoracion, json):
            # We must tell Django to grab fresh data from the database, or we'll
            # see our stale initial data and think our endpoint is broken!
            valoracion.refresh_from_db()
            
            data['user'] = valoracion.user
            data['post'] = valoracion.post
            expected = data
            assert_model_attrs(valoracion, expected)
            
            #Prueba la estructura del json
            TestValoracionViewSet.check_structure(valoracion, json)
            
            
    class TestUpdateOwner(
        UsesPatchMethod,
        UsesDetailEndpoint,
        AsUser('user'),
        Returns200,
    ):
        data = lambda_fixture(
            lambda post: {
                'rating': random.randint(1, 5),
                'comment': lorem.sentence(),
                'post': TestValoracionViewSet.base_url 
                    + url_for('post-detail', post.id),   
            }
        )
        
        def test_update_changes(self, data, valoracion, json):
            # We must tell Django to grab fresh data from the database, or we'll
            # see our stale initial data and think our endpoint is broken!
            valoracion.refresh_from_db()
            
            data['user'] = valoracion.user
            data['post'] = valoracion.post
            expected = data
            assert_model_attrs(valoracion, expected)
            
            #Prueba la estructura del json
            TestValoracionViewSet.check_structure(valoracion, json)

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
        valoraciones = lambda_fixture(
            lambda user, post: [
                Valoracion.objects.create(rating=rating, comment=comment,
                                          fecha_registro=timezone.now(), 
                                          post=post, user=user)
                for rating, comment in [
                    (1, 'Comment asd'),
                    (2, 'Comment   asdf asdfasd'),
                    (5, 'Comment   asdf asdfasd'),
                    (4, 'Comment   f asdfasd'),
                    (3, 'Comment   asdf assd'),
                ]
            ],
            autouse=True,
        )
        
        initial_valoraciones_ids = precondition_fixture(
            lambda valoraciones, valoracion:
                set(Valoracion.objects.values_list('id', flat=True)
            ), async_=False
        )

        def test_it_deletes_post(self, initial_valoraciones_ids, valoracion):
            expected = initial_valoraciones_ids - {valoracion.id}
            actual = set(Valoracion.objects.values_list('id', flat=True))
            assert expected == actual
    
    class TestDestroyOwner(
        UsesDeleteMethod,
        UsesDetailEndpoint,
        AsUser('user'),
        Returns204,
    ):
        valoraciones = lambda_fixture(
            lambda user, post: [
                Valoracion.objects.create(rating=rating, comment=comment,
                                          fecha_registro=timezone.now(), 
                                          post=post, user=user)
                for rating, comment in [
                    (1, 'Comment asd'),
                    (2, 'Comment   asdf asdfasd'),
                    (5, 'Comment   asdf asdfasd'),
                    (4, 'Comment   f asdfasd'),
                    (3, 'Comment   asdf assd'),
                ]
            ],
            autouse=True,
        )
        
        initial_valoraciones_ids = precondition_fixture(
            lambda valoraciones, valoracion:
                set(Valoracion.objects.values_list('id', flat=True)
            ), async_=False
        )

        def test_it_deletes_post(self, initial_valoraciones_ids, valoracion):
            expected = initial_valoraciones_ids - {valoracion.id}
            actual = set(Valoracion.objects.values_list('id', flat=True))
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
    
    class TestOrdenacionFechaRegistro(
        APIViewTest,
        UsesGetMethod,
        Returns200,
    ):
        @pytest.fixture
        def url(self):
            return url_for('valoracion-list') + '?ordering=fecha_registro'
        
        valoraciones = lambda_fixture(
            lambda user, post: [
                Valoracion.objects.create(rating=rating, comment=comment,
                                            fecha_registro=timezone.now(), 
                                            post=post, user=user)
                for rating, comment in [
                    (1, 'Comment asd'),
                    (2, 'Comment   asdf asdfasd'),
                    (5, 'Comment   asdf asdfasd'),
                    (4, 'Comment   f asdfasd'),
                    (3, 'Comment   asdf assd'),
                ]
            ],
            autouse=True,
        )
        
        class TestDescending(
            APIViewTest,
            UsesGetMethod,
        ):
            @pytest.fixture
            def url(self):
                return url_for('valoracion-list') + '?ordering=-fecha_registro'
            
            def test_it_orders_properly_desc(self, json, valoraciones):
                expected = express_valoraciones(sorted(valoraciones,
                                                    key=lambda valoracion: valoracion.fecha_registro,
                                                    reverse=True),
                                        TestValoracionViewSet.base_url)
                actual = json
                assert expected == actual
            
        def test_it_orders_properly_asc(self, json, valoraciones):
            expected = express_valoraciones(sorted(valoraciones,
                                                   key=lambda valoracion: valoracion.fecha_registro,
                                                   reverse=False),
                                     TestValoracionViewSet.base_url)
            actual = json
            assert expected == actual
            