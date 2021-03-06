#!/usr/bin/env python

from time import sleep
import random
from urllib import urlencode
import requests
from rarmy import data
import json

REDDIT_API_BASE = 'http://www.reddit.com/api/'

class Army(object):
    """
    Represents a set of soldiers, which are logged-in Reddit accounts.
    """
    def __init__(self, size=5):
        """
        Initializes an army of a given size. Uses army.json and accounts.json to
        find the account info.
        """
        self.soldiers = []

        # Load cached soldiers
        try:
            with open('config/army.json', 'r') as f:
                army = json.load(f)

            # Load army from the cached one
            for sdata in army:
                self.soldiers += [Soldier(sdata['acct'], sdata['session'])]
                # Check if we have enough accts
                if len(self.soldiers) == size:
                    return
        except IOError:
            pass # IDGAF

        # Apparently we don't have enough accts. Login more!
        users = [ a.acct['user'] for a in self.soldiers ]
        accts = [ a for a in data.accts if a['user'] not in users ]
        accts_len = len(accts)
        req = size - len(self.soldiers)

        # Not enough accts error
        if accts_len < req:
            new_len = len(self.soldiers) + accts_len
            print 'Not enough accounts for an army of size %d! Size will be decreased to %d.' % (size, new_len)
            req = accts_len
        # Too many accts, pick randomly from the remaining ones
        elif accts_len > req:
            accts = random.sample(accts, req)

        # Log in the remaining accts
        for x in xrange(req):
            s = Soldier(accts[x])
            while True:
                if s.login():
                    print 'LOGIN %s via %s' % (s.acct['user'], s.proxy)
                    sleep(2) # Avoid rate limit
                    break

            self.soldiers += [s]

        # Save the army that took so long to make
        self.save()

    def save(self):
        """
        Saves this army to a file.
        """
        with open('config/army.json', 'w') as f:
            json.dump([ {
                'acct': s.acct,
                'session': {
                    'modhash': s.modhash,
                    'cookies': s.cookies()
                }
            } for s in self.soldiers ], f)

    def random_soldier(self):
        """
        Retrieves a random soldier.
        """
        return random.choice(self.soldiers)

    def vote(self, name, dir=1, interval=60):
        """
        Votes on the given post.
        """
        if not type in [1, 2, 3]:
            print 'Unexpected error: Type must be 1, 2, or 3'
            raise

        for i, s in enumerate(self.soldiers):
            while True:
                if s.vote(name):
                    print 'VOTE %s %s %d' % (s.acct['user'], name, dir)
                    if i == len(self.soldiers) - 1:
                        return
                    sleep(60)
                    break

                print 'ERR_VOTE_RATELIMIT %s %s %d' % (s.acct['user'], name, dir)
                s.get_new_proxy()

class Soldier(object):
    """
    Represents an account.
    """
    def __init__(self, acct, session=None):
        self.acct = acct
        self.useragent = random.choice(data.useragents)

        # Load our session
        if session:
            self.modhash = session['modhash']
            cookies = requests.utils.cookiejar_from_dict(session['cookies'])
            self.session = requests.Session()
            self.session.cookies = cookies
        else:
            self.modhash = None
            self.session = requests.session()

        self.get_new_proxy()

    def params(self, args):
        """
        Gets the params passed in this soldier's requests.
        """
        headers = {}
        headers['User-Agent'] = self.useragent
        if self.modhash:
            headers['X-Modhash'] = self.modhash

        if 'proxy' in args and not args['proxy']:
            proxies = None
        else:
            proxies = { 'http': 'http://' + self.proxy } if self.proxy else {}

        return {
            'headers': headers,
            'proxies': proxies
        }

    def get(self, path, **kwargs):
        """
        Sends a GET request to Reddit.
        """
        while True:
            try:
                params = self.params(kwargs)
                return self.session.get(REDDIT_API_BASE + path, **params)
            except:
                self.get_new_proxy()
                print 'ERR_PROXY_GET %s Retrying with new proxy %s' % (self.acct['user'], self.proxy)
                sleep(2) # Avoid rate limit

    def post(self, path, payload={}, **kwargs):
        """
        Sends a POST request to Reddit.
        """
        while True:
            try:
                params = self.params(kwargs)
                params['headers']['Content-Type'] = 'application/x-www-form-urlencoded'
                return self.session.post(REDDIT_API_BASE + path, data=urlencode(payload), timeout=10, **params)
            except:
                self.get_new_proxy()
                print 'ERR_PROXY_POST %s Retrying with new proxy %s' % (self.acct['user'], self.proxy)
                sleep(2) # Avoid rate limit

    def get_new_proxy(self):
        """
        Gets a new proxy for this soldier.
        """
        self.proxy = data.proxies.random_proxy()

    def me(self):
        """
        Gets info about the user.
        """
        try:
            return self.get('me.json').json()
        except:
            return None

    def login(self):
        """
        Logs in the account. Nothing else works unless this has already been called successfully.
        The given proxy is set for this soldier if the login was successful via that proxy.

        @return The modhash if the login was successful
        """
        payload = {
            'api_type': 'json',
            'passwd': self.acct['pass'],
            'rem': True,
            'user': self.acct['user']
        }

        r = None
        while r is None:
            r = self.post('login', payload, proxy=False)
            try:        
                self.modhash = r.json()['json']['data']['modhash']
            except:
                r = None

        return self.modhash

    def cookies(self):
        """
        Gets the dict representation of this soldier's cookies.
        """
        return requests.utils.dict_from_cookiejar(self.session.cookies)

    def submit(self, title, sr, captcha, **kwargs):
        """
        Submits a post.
        """
        if 'kind' in kwargs:
            kind = kwargs['kind']
        else:
            kind = 'link'

        text = kwargs['text'] if 'text' in kwargs else None
        url = kwargs['url'] if 'url' in kwargs else None

        payload = {
            'api_type': 'json',
            'captcha': captcha[1],
            'iden': captcha[0],
            'kind': kind,
            'resubmit': True,
            'save': True,
            'sendreplies': True,
            'sr': sr,
            'text': text,
            'then': 'comments',
            'title': title,
            'url': url
        }

        r = self.post('submit', payload)
        try:
            return r.json()['json']['data']
        except: # No response
            return False

    def comment(self, parent, text):
        """
        Comments on a given post.
        """
        payload = {
            'api_type': 'json',
            'text': text,
            'thing_id': parent
        }

        r = self.post('comment', payload)
        try:
            return r.json()['json']['data']['things'][0]['data']
        except:
            return False

    def vote(self, id, dir=1):
        """
        Sends a vote.
        """
        payload = {
            'dir': dir,
            'id': id,
            'uh': self.modhash
        }

        r = self.post('vote', payload)
        return not 'RATELIMIT' in r.text
