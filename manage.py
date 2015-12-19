from __future__ import print_function
from webserver import create_app
import click

cli = click.Group()


@cli.command()
@click.option("--host", "-h", default="0.0.0.0", show_default=True)
@click.option("--port", "-p", default=8080, show_default=True)
@click.option("--debug", "-d", type=bool,
              help="Turns debugging mode on or off. If specified, overrides "
                   "'DEBUG' value in the config file.")
def runserver(host, port, debug):
    create_app().run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    cli()
