kerberosauthenticator
=====================

An Authenticator_ for JupyterHub_ that authenticates using Kerberos_.

.. contents:: :local:


Installation
------------

``kerberosauthenticator`` should be installed in the same Python environment as
the JupyterHub server.

**Install with Pip:**

.. code::

    pip install jupyterhub-kerberosauthenticator

**Install from source:**

.. code::

    pip install git+https://github.com/jcrist/kerberosauthenticator.git


Configuration
-------------

Kerberos authentication requires a keytab for the ``HTTP`` service principle
for the host running JupyterHub. Keytabs can be created on the command-line as
follows:

.. code-block:: shell

    $ kadmin -q "addprinc -randkey HTTP/FQDN"
    $ kadmin -q "xst -norandkey -k HTTP.keytab HTTP/FQDN"

where ``FQDN`` is the `fully qualified domain name`_ of the host running
JupyterHub. This keytab should be readable only by admins and other services
that may need it, and is typically stored with the JupyterHub configuration at
``/etc/jupyterhub/HTTP.keytab``:

.. code-block:: shell

    # Move the keytab to some expected location
    $ mv HTTP.keytab /etc/jupyterhub/HTTP.keytab

    # Make the keytab readable/writable only by jupyterhub and the admin group
    $ chmod 440 /etc/jupyterhub/HTTP.keytab
    $ chown jupyterhub:admin /etc/jupyterhub/HTTP.keytab

To enable ``kerberosauthenticator``, add the following lines to your
``jupyterhub_config.py``:

.. code-block:: python

    c.JupyterHub.authenticator_class = 'kerberosauthenticator.KerberosAuthenticator'
    c.JupyterHub.keytab = '/etc/jupyterhub/HTTP.keytab'

For many systems these parameters will be sufficient. Authenticators_ support
several other options such as whitelists or post-auth hooks. For more
information on all configuration options, see :doc:`options`.


Enabling Kerberos Authentication in Your Browser
------------------------------------------------

For Kerberos authentication to work properly, you usually have to enable
support for it in your browser. For more information see `this guide from
Cloudera`_.


Additional Resources
--------------------

If you're interested in ``kerberosauthenticator``, you may also be interested
in a few other libraries:

- ldapauthenticator_: A JupyterHub authenticator that uses LDAP_.

- jhub_remote_user_authenticator_: A JupyterHub authenticator that uses the
  ``REMOTE_USER`` header, intended to be used with authenticaticating proxies.

A (not complete) list of other authenticators can be found in the `JupyterHub
Wiki`_.

.. toctree::
    :maxdepth: 2
    :hidden:

    options.rst


.. _Authenticator:
.. _Authenticators: https://jupyterhub.readthedocs.io/en/stable/reference/authenticators.html
.. _Kerberos: https://web.mit.edu/kerberos/
.. _JupyterHub: https://jupyterhub.readthedocs.io/en/stable/
.. _fully qualified domain name: https://en.wikipedia.org/wiki/Fully_qualified_domain_name
.. _this guide from Cloudera: https://www.cloudera.com/documentation/enterprise/5-12-x/topics/cdh_sg_browser_access_kerberos_protected_url.html
.. _ldapauthenticator: https://github.com/jupyterhub/ldapauthenticator
.. _LDAP: https://en.wikipedia.org/wiki/Lightweight_Directory_Access_Protocol
.. _jhub_remote_user_authenticator: https://github.com/cwaldbieser/jhub_remote_user_authenticator
.. _JupyterHub Wiki: https://github.com/jupyterhub/jupyterhub/wiki/Authenticators
