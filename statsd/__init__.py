"""
Originally written by James Socol
https://github.com/jsocol/pystatsd

Modified by Shreyans Bhansali at Venmo
21 April 2012
"""
import sys; import os; APPROOT = os.environ.get('APPROOT') or '/ebs/appvenmo'; sys.path.append(APPROOT);

import venmo_constants

from lib.utils import get_stage

from client import StatsClient

__all__ = ['StatsClient', 'statsd']

VERSION = (0, 5, 0)
__version__ = '.'.join(map(str, VERSION))

statsd = None

host = venmo_constants.STATSD_HOST
port = getattr(venmo_constants, 'STATSD_PORT', 8125)
prefix = get_stage(APPROOT)
statsd = StatsClient(host, port, prefix)
