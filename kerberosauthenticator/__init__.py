from .auth import KerberosAuthenticator, KerberosLocalAuthenticator

try:
    from ._version import __version__
except ImportError:
    __version__ = "UNKNOWN"

__all__ = [
  "__version__",
  "KerberosAuthenticator",
  "KerberosLocalAuthenticator"
]
