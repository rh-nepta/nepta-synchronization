from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

__author__ = "Adam Okuliar"
__email__ = "aokuliar@redhat.com"

from . import client
from . import server

