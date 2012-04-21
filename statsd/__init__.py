import venmo_constants

from client import StatsClient

__all__ = ['StatsClient', 'statsd']

VERSION = (0, 5, 0)
__version__ = '.'.join(map(str, VERSION))

statsd = None

host = venmo_constants.STATSD_HOST
port = venmo_constants.STATSD_PORT
prefix = getattr(venmo_constants, 'STATSD_PREFIX', None)
statsd = StatsClient(host, port, prefix)
