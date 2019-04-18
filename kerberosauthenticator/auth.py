import os

import kerberos
from jinja2 import ChoiceLoader, FileSystemLoader
from jupyterhub.auth import Authenticator
from jupyterhub.handlers import BaseHandler
from jupyterhub.utils import url_path_join
from tornado import web
from traitlets import Unicode


TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')


class KerberosLoginHandler(BaseHandler):
    _loaded = False

    def __init__(self, *args, **kwargs):
        if KerberosLoginHandler._loaded:
            return
        super().__init__(*args, **kwargs)

        self.log.debug('Adding %s to template path', TEMPLATE_DIR)
        loader = FileSystemLoader([TEMPLATE_DIR])
        env = self.settings['jinja2_env']
        previous_loader = env.loader
        env.loader = ChoiceLoader([previous_loader, loader])
        self._loaded = True

    def raise_auth_required(self):
        self.set_status(401)
        data = self.render_template(
            'kerberos_login_error.html',
            login_url=self.settings['login_url']
        )
        self.write(data)
        self.set_header("WWW-Authenticate", "Negotiate")
        raise web.Finish()

    async def get(self):
        auth_header = self.request.headers.get('Authorization')
        if not auth_header:
            self.raise_auth_required()

        auth_type, auth_key = auth_header.split(" ", 1)
        if auth_type != 'Negotiate':
            self.raise_auth_required()

        # Headers are of the proper form, initialize login routine
        user = await self.login_user()
        if user is None:
            raise web.HTTPError(403)
        else:
            # Logged in, redirect to next url
            self.redirect(self.get_next_url(user))


class KerberosAuthenticator(Authenticator):
    """
    Kerberos Authenticator for JupyterHub
    """

    service_name = Unicode(
        "HTTP",
        help="""The service's kerberos principal name.

        This is almost always "HTTP" (the default)""",
        config=True
    )

    keytab = Unicode(
        "HTTP.keytab",
        help="The path to the keytab file",
        config=True
    )

    login_service = "kerberos"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        os.environ['KRB5_KTNAME'] = self.keytab

    def get_handlers(self, app):
        return [('/kerberos_login', KerberosLoginHandler)]

    def login_url(self, base_url):
        return url_path_join(base_url, 'kerberos_login')

    async def authenticate(self, handler, data):
        auth_header = handler.request.headers.get('Authorization')
        if not auth_header:  # pragma: nocover
            self.log.error("authenticate hit with no kerberos credentials, "
                           "this code path should never occur")
            return None

        auth_type, auth_key = auth_header.split(" ", 1)
        if auth_type != 'Negotiate':  # pragma: nocover
            self.log.error("authenticate hit with no kerberos credentials, "
                           "this code path should never occur")
            return None

        gss_context = None
        try:
            # Initialize kerberos context
            rc, gss_context = kerberos.authGSSServerInit(self.service_name)

            # NOTE: Per the pykerberos documentation, the return code should be
            # checked after each step. However, after reading the pykerberos
            # code no method used here will ever return anything but
            # AUTH_GSS_COMPLETE (all other cases will raise an exception).  We
            # keep these checks in just in case pykerberos changes its behavior
            # to match its docs, but they likely never will trigger.
            if rc != kerberos.AUTH_GSS_COMPLETE:  # pragma: nocover
                self.log.error("GSS server init failed, return code = %r", rc)
                return None

            # Challenge step
            rc = kerberos.authGSSServerStep(gss_context, auth_key)
            if rc != kerberos.AUTH_GSS_COMPLETE:  # pragma: nocover
                # Only warn here, since this happens for any user failing login
                self.log.warn("GSS server step failed, return code = %r", rc)
                return None
            gss_key = kerberos.authGSSServerResponse(gss_context)

            # Retrieve user name
            fulluser = kerberos.authGSSServerUserName(gss_context)
            user = fulluser.split("@", 1)[0]

            # Complete the protocol by responding with the Negotiate header
            handler.set_header('WWW-Authenticate', "Negotiate %s" % gss_key)
            return user
        except kerberos.GSSError as err:  # pragma: nocover
            self.log.error("Error occurred during kerberos authentication",
                           exc_info=err)
            return None
        finally:
            if gss_context is not None:
                kerberos.authGSSServerClean(gss_context)
