"""
Originall written by James Socol
https://github.com/jsocol/pystatsd

Modified by Shreyans Bhansali at Venmo
21 April 2012
"""

from functools import wraps
import random
import socket
import time

class _Timer(object):
    """A context manager/decorator for statsd.timing()."""

    def __init__(self, client, stat, rate=1):
        self.client = client
        self.stat = stat
        self.rate = rate
        self.ms = None

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kw):
            with self:
                return f(*args, **kw)
        return wrapper

    def __enter__(self):
        self.start = time.time()
        return self

    def __exit__(self, typ, value, tb):
        dt = time.time() - self.start
        self.ms = int(round(1000 * dt))  # Convert to ms.
        self.client.timing(self.stat, self.ms, self.rate)


class _LogAttemptAndError(object):
    """A context manager/decorator that logs an attempt made to 
    run a function, and any error raised during the function's
    execution, used by stats.log_attempt_and_error().
    """

    def __init__(self, client, base_stat):
        self.client = client
        self.base_stat = base_stat

    def __call__(self, f):
        @wraps(f)
        def wrapper(*args, **kw):
            with self:
                return f(*args, **kw)
        return wrapper

    def __enter__(self):
        attempt_stat = "%s.attempt" % self.base_stat
        self.client.incr(attempt_stat)

    def __exit__(self, type, value, traceback):
        if isinstance(value, Exception):
            error_stat = "%s.error" % self.base_stat
            self.client.incr(error_stat)

class StatsClient(object):
    """A client for statsd."""

    def __init__(self, host='localhost', port=8125, prefix=None):
        """Create a new client."""
        # Use getaddrinfo to support IPv4/6.
        self._addr = socket.getaddrinfo(host, port)[0][4]
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self._prefix = prefix

    def timer(self, stat, rate=1):
        return _Timer(self, stat, rate)

    def timing(self, stat, delta, rate=1):
        """Send new timing information. `delta` is in milliseconds."""
        self._send(stat, '%d|ms' % delta, rate)

    def incr(self, stat, count=1, rate=1):
        """Increment a stat by `count`."""
        self._send(stat, '%d|c' % count, rate)

    def decr(self, stat, count=1, rate=1):
        """Decrement a stat by `count`."""
        self.incr(stat, -count, rate)

    def gauge(self, stat, value, rate=1):
        """Set a gauge value."""
        self._send(stat, '%d|g' % value, rate)

    def log_attempt_and_error(self, base_stat):
        return _LogAttemptAndError(self, base_stat)

    def _send(self, stat, value, rate=1):
        """Send data to statsd."""
        if rate < 1:
            if random.random() < rate:
                value = '%s|@%s' % (value, rate)
            else:
                return

        if self._prefix:
            stat = '%s.%s' % (self._prefix, stat)

        try:
            self._sock.sendto('%s:%s' % (stat, value), self._addr)
        except socket.error:
            # No time for love, Dr. Jones!
            pass
