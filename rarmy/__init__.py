#!/usr/bin/env python

from time import sleep
import random
from urllib import urlencode
import requests
from rarmy import data

REDDIT_API_BASE = 'http://www.reddit.com/api/'

class Army(object):
    """
    Represents a set of soldiers, which are logged-in Reddit accounts.
    """
    def __init__(self, size=50):
        accts = data.accts
        accts_len = len(accts)
        if accts_len < size:
            print 'Not enough accounts for an army of size ' + str(size) + '! Size will be decreased to ' + str(accts_len) + '.'
            size = accts_len
        elif accts_len > size:
            accts = random.sample(accts, size)

        self.soldiers = []
        for x in xrange(size):
            s = Soldier(accts[x])
            while True:
                if s.login():
                    print 'LOGIN ' + s.acct['user'] + ' via ' + s.proxy
                    break

            self.soldiers.append(s)
        print '== ARMY INITIALIZED WITH ' + str(len(self.soldiers)) + ' SOLDIERS =='

    def random_soldier(self):
        """
        Retrieves a random soldier.
        """
        return random.choice(self.soldiers)

    def vote(self, id, type=3, dir=1, interval=60):
        """
        Votes on the given post.
        """
        if not type in [1, 2, 3]:
            print 'Unexpected error: Type must be 1, 2, or 3'
            raise

        for s in self.soldiers:
            while True:
                if s.vote('t' + str(type) + '_' + id):
                    print 'VOTE ' + s.acct['user'] + ' ' + id + ' ' + str(dir)
                    sleep(interval)
                    break

                print 'ERR_VOTE_RATELIMIT ' + s.acct['user'] + ' ' + id + ' ' + str(dir)
                s.get_new_proxy()

class Soldier(object):
    """
    Represents an account.
    """
    def __init__(self, acct):
        self.acct = acct
        self.useragent = random.choice(data.useragents)
        self.modhash = None # The modhash. If logged in this will be set.
        self.get_new_proxy()
        self.client = requests.session()

    def params(self):
        """
        Gets the params passed in this soldier's requests.
        """
        headers = {}
        headers['User-Agent'] = self.useragent
        if self.modhash:
            headers['X-Modhash'] = self.modhash
        proxies = { 'http': 'http://' + self.proxy } if self.proxy else {}
        return {
            'headers': headers,
            'proxies': proxies
        }

    def get(self, path, **kwargs):
        """
        Sends a GET request to Reddit.
        """
        params = self.params()
        while True:
            try:
                return self.client.get(REDDIT_API_BASE + path, **params)
            except:
                self.get_new_proxy()
                print 'ERR_PROXY_GET ' + self.acct['user'] + ' Retrying with new proxy ' + self.proxy
                params['proxies'] = { 'http': 'http://' + self.proxy }
                sleep(2) # Avoid rate limit

    def post(self, path, payload={}, **kwargs):
        """
        Sends a POST request to Reddit.
        """
        params = self.params()
        params['headers']['Content-Type'] = 'application/x-www-form-urlencoded'
        while True:
            try:
                return self.client.post(REDDIT_API_BASE + path, data=urlencode(payload), timeout=3, **params)
            except:
                self.get_new_proxy()
                print 'ERR_PROXY_POST ' + self.acct['user'] + ' Retrying with new proxy ' + self.proxy
                params['proxies'] = { 'http': 'http://' + self.proxy }
                sleep(2) # Avoid rate limit

    def get_new_proxy(self):
        """
        Gets a new proxy for this soldier.
        """
        self.proxy = data.proxies.random_proxy()

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
            r = self.post('login', payload)
            try:        
                self.modhash = r.json()['json']['data']['modhash']
            except:
                r = None

        return self.modhash

    def submit(self, title, sr, captcha, **kwargs):
        """
        Submits something.
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
        print r.text
        return r.text

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
