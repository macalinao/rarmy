#!/usr/bin/env python

from time import sleep
import random
from urllib import urlencode
import requests
from rarmy import data

REDDIT_API_BASE = 'http://www.reddit.com/api/'

class Army(object):
    def __init__(self, size=50):
        accts = data.accts
        accts_len = len(accts)
        if accts_len < size:
            print 'Not enough accounts for an army of size ' + str(size) + '! Size will be decreased to ' + str(accts_len) + '.'
            size = accts_len

        self.soldiers = []
        for x in xrange(size):
            s = Soldier(accts[x])
            while True:
                if s.login():
                    print 'LOGIN ' + s.acct['user'] + ' via ' + s.proxy
                    break

            self.soldiers.append(s)
        print '== ARMY INITIALIZED WITH ' + str(len(self.soldiers)) + ' SOLDIERS =='

    def upvote_link(self, id, interval=60):
        for s in self.soldiers:
            s.vote('t3_' + id)
            print 'UPVOTE ' + s.acct['user'] + ' ' + id
            sleep(interval)

    def upvote_comment(self, id):
        for s in self.soldiers:
            s.get_submission(url).comments[0].upvote()

class Soldier(object):
    """
    Represents an account.
    """
    def __init__(self, acct):
        self.acct = acct
        self.useragent = random.choice(data.useragents)
        self.modhash = None # The modhash. If logged in this will be set.
        self.proxy = data.proxies.random_proxy()
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
        return self.client.get(REDDIT_API_BASE + path, **params)

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
                self.proxy = data.proxies.random_proxy()
                print 'ERR_POST ' + self.acct['user'] + ' Retrying with new proxy ' + self.proxy
                params['proxies'] = { 'http': 'http://' + self.proxy }

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
            return r.json()['json']['data']['name']
        except: # No response
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
        return r.text is '{}'
