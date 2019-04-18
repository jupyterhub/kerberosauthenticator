from urllib.parse import urlparse

import pytest
from jupyterhub.tests.mocking import public_url
from jupyterhub.tests.test_api import add_user
from jupyterhub.tests.utils import async_requests
from requests_kerberos import HTTPKerberosAuth


@pytest.mark.gen_test(timeout=60)
@pytest.mark.parametrize('auto_login', [True, False])
def test_integration(app, auto_login, logged_in):
    app.authenticator.auto_login = auto_login

    # Create a user
    add_user(app.db, app, name="alice")

    if auto_login:
        url = public_url(app, path="/hub/login")
        resp = yield async_requests.get(url)
        # Sends back 401 requesting authentication
        assert resp.status_code == 401
        # 401 page is formatted nicely
        assert "Failed to login with Kerberos." in resp.text
        assert resp.text.count("/hub/login") >= 2
        # Before that was a redirect to the auth handler
        assert resp.history[0].status_code == 302
        # Now use the redirected url with auth enabled
        location = resp.history[0].headers['location']
        netloc = urlparse(app.bind_url).netloc
        url = 'http://%s%s' % (netloc, location)
    else:
        url = public_url(app, path="/hub/kerberos_login")

    # Go through the login procedure
    resp = yield async_requests.get(
        url,
        auth=HTTPKerberosAuth(hostname_override="address.example.com")
    )

    if logged_in:
        # Successful
        resp.raise_for_status()

        # At user notebook, login successful
        assert resp.url.startswith(public_url(app, path="/user/alice"))
    else:
        # Unsuccessful
        assert resp.status_code == 401
