from main.serializers import ValoracionSerializer


def check_field(clase, name, type=None, max_length=None, pk=False,
                required=None, help_text=None, fk_model=None):
    field = clase._meta.get_field(name)
    #Comprueba existencia de campo
    assert field
    #Comprueba tipo de campo
    if type:
        assert isinstance(field, type)
    # Comprueba si es clave primaria
    if pk:
        assert field.primary_key
    # Comprueba longitud de campo
    if max_length:
        assert field.max_length == max_length
    if required is not None:
        assert isrequired(field) == required
    if help_text:
        assert field.help_text == help_text
    if fk_model:
        assert field.remote_field.model == fk_model
    

def isrequired(field):
    return field.blank is False and field.null is False

def get_field(serializer, field_name):
    
    return getattr(serializer, field_name) if hasattr(serializer, field_name) \
        else getattr(serializer.Meta, field_name) if hasattr(serializer.Meta, field_name) \
        else None