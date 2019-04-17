import os

import kerberos
from jupyterhub.auth import LocalAuthenticator
from jupyterhub.handlers import BaseHandler
from jupyterhub.utils import url_path_join
from tornado import web
from traitlets import Unicode


class KerberosLoginHandler(BaseHandler):
    def raise_auth_required(self):
        self.set_status(401)
        self.write('Authentication required')
        self.set_header("WWW-Authenticate", "Negotiate")
        raise web.Finish()

    async def get(self):
        auth_header = self.request.headers.get('Authorization')
        if not auth_header:
            self.raise_auth_required()

        auth_type, auth_key = auth_header.split(" ", 1)
        if auth_type != 'Negotiate':
            self.raise_auth_required()

        # Headers are of the proper form, bounce back to main login to do
        # actual auth in the main handler
        self.redirect(self.get_next_url())


class KerberosAuthenticator(LocalAuthenticator):
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
        if not auth_header:
            self.log.warn("authenticate hit with no kerberos credentials")
            return None

        auth_type, auth_key = auth_header.split(" ", 1)
        if auth_type != 'Negotiate':
            self.log.warn("authenticate hit with no kerberos credentials")
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
            if rc != kerberos.AUTH_GSS_COMPLETE:
                self.log.error("GSS server init failed, return code = %r", rc)
                return None

            # Challenge step
            rc = kerberos.authGSSServerStep(gss_context, auth_key)
            if rc != kerberos.AUTH_GSS_COMPLETE:
                self.log.error("GSS server step failed, return code = %r", rc)
                return None
            gss_key = kerberos.authGSSServerResponse(gss_context)

            # Retrieve user name
            fulluser = kerberos.authGSSServerUserName(gss_context)
            user = fulluser.split("@", 1)[0]

            # Complete the protocol by responding with the Negotiate header
            handler.set_header('WWW-Authenticate', "Negotiate %s" % gss_key)
            return user
        except kerberos.GSSError as err:
            self.log.error("Error occurred during kerberos authentication",
                           exc_info=err)
            return None
        finally:
            if gss_context is not None:
                kerberos.authGSSServerClean(gss_context)
