import os
import subprocess
import sys

import pytest
from jupyterhub.tests.conftest import io_loop
from jupyterhub.tests.mocking import MockHub

from kerberosauthenticator import KerberosAuthenticator

io_loop = io_loop

HTTP_KEYTAB = '/root/HTTP.keytab'
USERS_KEYTAB = '/root/users.keytab'


@pytest.fixture(scope="module")
def app(request, io_loop):
    app = MockHub(
        authenticator=KerberosAuthenticator(
            keytab=HTTP_KEYTAB
        ),
        cookie_secret=os.urandom(32),
        hub_ip="address.example.com"
    )

    async def make_app():
        await app.initialize([])
        await app.start()

    io_loop.run_sync(make_app)

    yield app

    # disconnect logging during cleanup because pytest closes captured FDs prematurely
    app.log.handlers = []
    MockHub.clear_instance()
    try:
        app.stop()
    except Exception as e:
        print("Error stopping Hub: %s" % e, file=sys.stderr)


@pytest.fixture(params=[True, False], ids=['logged_in=True', 'logged_in=False'])
def logged_in(request):
    kdestroy()
    if request.param:
        kinit()
    else:
        kdestroy()
    return request.param


def kinit(username='alice'):
    subprocess.check_call(["kinit", "-kt", USERS_KEYTAB, username])


def kdestroy():
    subprocess.check_call(["kdestroy"])
