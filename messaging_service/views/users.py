from ..models import User


@view_config(route_name='users')
def users(request):
    return {'foo': 'bar'}

