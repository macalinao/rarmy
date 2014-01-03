from lib import dbs, proxies
import praw
from time import sleep
import random

class Army(object):
    def __init__(self, size=50):
        accts = dbs.load_accts()
        accts_len = len(accts)
        if accts_len < size:
            print 'Not enough accounts for an army of size ' + str(size) + '! Size will be decreased to ' + str(accts_len) + '.'
            size = accts_len

        pm = proxies.ProxyManager()

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
    s.config.http_proxy = 'http://' + proxy
    s.login(acct['user'], acct['pass'])
    print 'LOGIN ' + acct['user'] + ' via ' + proxy
    return s
