import base64
import os

import gssapi
from gssapi.raw import acquire_cred_with_password
from gssapi.raw.misc import GSSError
from jinja2 import ChoiceLoader, FileSystemLoader
from jupyterhub.auth import Authenticator, LocalAuthenticator
from jupyterhub.handlers import BaseHandler
from jupyterhub.utils import socket, url_path_join
from tornado import web
from traitlets import Unicode

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


class KerberosLoginHandler(BaseHandler):
    _loaded = False

    def __init__(self, *args, **kwargs):
        if KerberosLoginHandler._loaded:
            return
        super().__init__(*args, **kwargs)

        self.log.debug("Adding %s to template path", TEMPLATE_DIR)
        loader = FileSystemLoader([TEMPLATE_DIR])
        env = self.settings["jinja2_env"]
        previous_loader = env.loader
        env.loader = ChoiceLoader([previous_loader, loader])
        self._loaded = True

    async def raise_auth_required(self):
        self.set_status(401)
        data = await self.render_template(
            "kerberos_login_error.html",
            login_url=self.settings["login_url"],
        )
        self.add_header("WWW-Authenticate", "Negotiate")
        self.add_header("WWW-Authenticate", "Basic")
        self.write(data)
        raise web.Finish()

    async def get(self):
        auth_header = self.request.headers.get("Authorization")
        if not auth_header:
            await self.raise_auth_required()

        auth_type, auth_key = auth_header.split(" ", 1)
        if auth_type != "Negotiate" and auth_type != "Basic":
            await self.raise_auth_required()

        # Headers are of the proper form, initialize login routine
        user = await self.login_user()
        if user is None:
            raise web.HTTPError(401)
        else:
            # Logged in, redirect to next url
            self.redirect(self.get_next_url(user))


class KerberosAuthenticator(Authenticator):
    """
    Kerberos Authenticator for JupyterHub
    """

    service_name = Unicode(
        f"HTTP/{socket.gethostname().lower()}",
        help="""Kerberos SPN (Server Principal Name).

        This should normally be HTTP/<hostname>""",
        config=True
    )

    keytab = Unicode("HTTP.keytab", help="The path to the keytab file", config=True)

    login_service = "kerberos"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        os.environ["KRB5_KTNAME"] = self.keytab

    def get_handlers(self, app):
        return [("/kerberos_login", KerberosLoginHandler)]

    def login_url(self, base_url):
        return url_path_join(base_url, "kerberos_login")

    async def authenticate(self, handler, data):
        auth_header = handler.request.headers.get("Authorization")
        if not auth_header:  # pragma: nocover
            self.log.error(
                "authenticate hit with no kerberos credentials, "
                "this code path should never occur"
            )
            return None

        auth_type, auth_key = auth_header.split(" ", 1)

        server_name = gssapi.Name(self.service_name)
        server_creds = gssapi.Credentials(usage='accept', name=server_name)
        server_ctx = gssapi.SecurityContext(usage='accept', creds=server_creds)

        try:
            if auth_type == "Negotiate":
                in_token = base64.b64decode(auth_key)
                out_token = server_ctx.step(in_token)
                if not server_ctx.complete:
                    self.log.warn("GSS server step failed")
                    return None
                handler.set_header("WWW-Authenticate", "Negotiate %s" % base64.b64encode(out_token).decode('ascii'))
            elif auth_type == "Basic":
                user, password = base64.b64decode(auth_key).split(b':', 1)
                user = user.decode('ascii')
                client_name = gssapi.Name(user)
                client_creds = acquire_cred_with_password(client_name, password).creds
                client_ctx = gssapi.SecurityContext(usage='initiate', name=server_name, creds=client_creds)
                client_ctx.step(server_ctx.step(client_ctx.step()))
                if not client_ctx.complete or not server_ctx.complete:
                    self.log.warn("GSS client/server step failed for password auth")
                    return None
            else:
                self.log.error(
                    "authenticate hit with no kerberos credentials, "
                    "this code path should never occur"
                )
                return None
            user = str(server_ctx.initiator_name).split('@', 1)[0]
            return user
        except GSSError as e:
            self.log.error("Error occurred during kerberos authentication", exc_info=e)
            return None


class KerberosLocalAuthenticator(LocalAuthenticator, KerberosAuthenticator):
    """
    Kerberos local authenticator for JupyterHub

    Checks for local users, and can attempt to create them if they don't exist.
    """
