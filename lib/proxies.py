from lib import dbs
import time

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
        if proxies is None:
            self.proxies = dbs.load_proxies()
        else:
            self.proxies = proxies

        self.next = 0
        self.proxy_times = {}

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
            return 'https://' + proxy

        # Proxy unavailable, return the waiting time.
        return -diff
