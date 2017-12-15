import click
import requests


class Context:
    def __init__(self):
        url_scheme = "https://" if click.confirm("Use HTTPS?") else "http://"
        address = click.prompt(
            "What is the address of the service instance?",
            default="localhost"
        )
        port = click.prompt(
            "What is the port of the service instance?",
            default="6543"
        )
        self.address = "{scheme}{address}:{port}/".format(
            scheme=url_scheme,
            address=address,
            port=port,
        )
        self.session = requests.session()

        self.state = {}

    def authorization(self, username):
        return "JWT {}".format(
            self.state['users'][username]['token']
        )

    def get(self, endpoint, *args, **kwargs):
        return self.session.get(self.address + endpoint, *args, **kwargs)

    def post(self, endpoint, *args, **kwargs):
        return self.session.post(self.address + endpoint, *args, **kwargs)


context = Context()
