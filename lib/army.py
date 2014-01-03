from lib import dbs, proxies
from time import sleep
import random
from urllib import urlencode
import requests

API_BASE = 'http://www.reddit.com/api/'

class Army(object):
    def __init__(self, size=50):
        accts = dbs.load_accts()
        accts_len = len(accts)
        if accts_len < size:
            print 'Not enough accounts for an army of size ' + str(size) + '! Size will be decreased to ' + str(accts_len) + '.'
            size = accts_len

        pm = proxies.ProxyManager()
        useragents = dbs.load_useragents()

        self.soldiers = []
        for x in xrange(size):
            self.soldiers.append(create_soldier(accts[x], pm.random_proxy()))
        print '== ARMY INITIALIZED WITH ' + str(len(self.soldiers)) + ' SOLDIERS =='

    def upvote_submission(self, url):
        for s in self.soldiers:
            sub = s.get_submission(url)
            sub.upvote()
            print 'UPVOTE ' + s.user.name + ' ' + sub.title
            sleep(60)

    def upvote_comment(self, url):
        for s in self.soldiers:
            s.get_submission(url).comments[0].upvote()

def create_soldier(acct, proxy):
    """
    Creates a soldier.
    """
    s = praw.Reddit('reddit-army 1.0 by GrievingSpain')
    s.config.http_proxy = 'http://' + '1.2.3.4'
    s.login(acct['user'], acct['pass'])
    print 'LOGIN ' + acct['user'] + ' via ' + proxy
    return s

class Soldier(object):
    """
    Represents an account.
    """
    def __init__(self, acct, useragent='MSIE (MSIE 6.0; X11; Linux; i686) Opera 7.23'):
        self.acct = acct
        self.useragent = useragent
        self.modhash = None # The modhash. If logged in this will be set.
        self.proxy = None

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
        return self.client.get(API_BASE + path, **params)

    def post(self, path, payload={}, **kwargs):
        """
        Sends a POST request to Reddit.
        """
        params = self.params()
        params['headers']['Content-Type'] = 'application/x-www-form-urlencoded'
        return self.client.post(API_BASE + path, data=urlencode(payload), **params)

    def login(self, proxy=None):
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

        self.proxy = proxy
        r = self.post('login', payload)
        try:
            self.modhash = r.json()['json']['data']['modhash']
        except:
            self.proxy = None
            return False

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
            'uh': self.modhash,
            'url': url
        }

        r = self.post('submit', payload)
        print r.text
