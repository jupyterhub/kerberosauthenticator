import os
import subprocess
import sys

import pytest
from jupyterhub.tests.conftest import io_loop
from jupyterhub.tests.mocking import MockHub

from kerberosauthenticator import KerberosAuthenticator

io_loop = io_loop


@pytest.fixture(scope="module")
def app(request, io_loop):
    app = MockHub(
        authenticator=KerberosAuthenticator(
            keytab='/home/testuser/HTTP.keytab',
        ),
        cookie_secret=os.urandom(32),
        hub_ip="edge.example.com"
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


def kinit():
    subprocess.check_call([
        "kinit", "-kt", '/home/testuser/testuser.keytab', 'testuser'
    ])


def kdestroy():
    subprocess.check_call(["kdestroy"])
