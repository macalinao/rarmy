from lib import dbs
import time
import random

class ProxyManager(object):
    """
    Manages a set of HTTPS proxies.
    """
    def __init__(self, cooldown=600, proxies=None):
        """
        Initializes this ProxyManager.

        @param cooldown The time until a proxy can be used again.
        """
        self.cooldown = cooldown
        print 'Loading proxies...'
        if proxies is None:
            self.proxies = dbs.load_proxies()
        else:
            self.proxies = proxies
        print 'Proxies loaded.'

        self.next = 0
        self.proxy_times = {}

    def random_proxy(self):
        """
        Gets a random proxy. This will only work if you have a huge proxy list.
        """
        return random.choice(self.proxies)

    def next_proxy(self):
        """
        Gets the next proxy to use. If no available proxies, returns the time
        in seconds until the next proxy is available.
        """
        proxy = self.proxies[self.next]
        now = time.time()
        diff = now - self.proxy_times.get(proxy, -1) + self.cooldown

        # Proxy available; return it.
        if diff > 0:
            self.proxy_times[proxy] = time.time()
            self.next += 1
            if self.next == len(self.proxies): self.next = 0
            return proxy

        # Proxy unavailable, return the waiting time.
        return -diff
