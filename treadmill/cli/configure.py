"""Manage Treadmill app manifest.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import logging

import click

from .. import cli
from treadmill import restclient
from treadmill import context
from treadmill import yamlwrapper as yaml


_LOGGER = logging.getLogger(__name__)

_FORMATTER = cli.make_formatter('app')

_APP_REST_PATH = '/app/'


def _configure(apis, manifest, appname):
    """Configure a Treadmill app"""
    try:
        existing = restclient.get(apis, _APP_REST_PATH + appname).json()

    except restclient.NotFoundError:
        if not manifest:
            raise
        else:
            existing = None

    if manifest:
        with io.open(manifest, 'rb') as fd:
            app = yaml.load(stream=fd)
        if existing:
            restclient.put(apis, _APP_REST_PATH + appname, payload=app)
        else:
            restclient.post(apis, _APP_REST_PATH + appname, payload=app)

        # Get new value after update.
        existing = restclient.get(apis, _APP_REST_PATH + appname).json()

    cli.out(_FORMATTER(existing))


def _delete(apis, appname):
    """Deletes the app by name."""
    restclient.delete(apis, _APP_REST_PATH + appname)
    return None


def _list(apis):
    """List configured apps."""
    response = restclient.get(apis, _APP_REST_PATH)
    cli.out(_FORMATTER(response.json()))


def init():
    """Return top level command handler."""

    @click.command()
    @click.option('--api', required=False, help='API url to use.',
                  envvar='TREADMILL_RESTAPI')
    @click.option('-m', '--manifest', help='App manifest file (stream)',
                  type=click.Path(exists=True, readable=True))
    @click.option('--delete', help='Delete the app.',
                  is_flag=True, default=False)
    @click.argument('appname', required=False)
    @cli.handle_exceptions(restclient.CLI_REST_EXCEPTIONS)
    def configure(api, manifest, delete, appname):
        """Configure a Treadmill app"""
        restapi = context.GLOBAL.admin_api(api)
        if appname:
            if delete:
                return _delete(restapi, appname)
            return _configure(restapi, manifest, appname)
        else:
            return _list(restapi)

    return configure
