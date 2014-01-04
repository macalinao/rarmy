import time
import random
import json

class Namegen(object):
    """
    Generates random account usernames.
    """
    def __init__(self, limit=20):
        self.adjectives = try_parse_newline_file('txt/adjectives.txt')
        self.nouns = try_parse_newline_file('txt/nouns.txt')
        self.limit = limit

    def generate(self):
        """
        Generates the account name.
        """
        while True:
            user = random.choice(self.adjectives).title() + random.choice(self.nouns).title()
            if len(user) <= self.limit: break
        return user

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
            self.proxies = try_parse_newline_file('config/proxies.txt')
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

class CaptchaManager(object):
    """
    Manages our CAPTCHAs.txt
    """
    def __init__(self):
        lines = try_parse_newline_file('config/captchas.txt')
        self.captchas = [ c.split('=') for c in lines ]

    def next(self, amt=1):
        """
        Gets the next number of CAPTCHAs. If there aren't enough CAPTCHAs,
        the maximum amount of captchas are returned.
        """
        ret = []
        for x in xrange(amt):
            if len(self.captchas) > 0:
                ret.append(self.captchas.pop())
            else:
                break

        self.save()
        return ret if len(ret) > 0 else None

    def add(self, captchas):
        """
        Adds CAPTCHAs to the CAPTCHA manager. It will save it to our
        captchas.txt file.
        """
        self.captchas += captchas
        self.save()

    def save(self):
        """
        Saves our captchas.
        """
        with open('config/captchas.txt', 'w') as f:
            f.write('\n'.join(c[0] + '=' + c[1] for c in self.captchas))

def _load_accts():
    """
    Loads accts.
    """
    try:
        with open('config/accounts.json', 'r') as f:
            return json.load(f)
    except IOError:
        print 'Accounts file could not be loaded!'
        return []

def try_parse_newline_file(file):
    """
    Parses a newline file, with a message if it doesn't work, returning an empty list.
    """
    try:
        return parse_newline_file(file)
    except IOError:
        print 'File ' + file + ' does not exist!'
        return []

def parse_newline_file(file):
    """
    Parses a newline-delimited file, given the file's name, returning
    each non-empty line with leading and trailing whitespace removed.
    """
    with open(file, 'r') as f:
        return [ l.strip() for l in f.read().split('\n') if l ]

proxies = ProxyManager()
ng = Namegen()
captchas = CaptchaManager()
useragents = try_parse_newline_file('txt/useragents.txt')
accts = _load_accts()
