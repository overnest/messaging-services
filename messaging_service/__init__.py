from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from pyramid.renderers import JSON


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.include('.models')
    config.include('.routes')
    config.add_renderer('json', JSON(indent=2))

    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.include('pyramid_jwt')
    config.set_jwt_authentication_policy(settings['jwt.signature'])

    config.scan()
    return config.make_wsgi_app()
