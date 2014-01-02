#!/usr/bin/env python

import random
from lib import dbs

class Namegen(object):
    """
    Generates random account usernames.
    """
    def __init__(self, limit=20):
        self.adjectives = dbs.load_adjectives()
        self.nouns = dbs.load_nouns()
        self.limit = limit

    def generate(self):
        """
        Generates the account name.
        """
        while True:
            user = random.choice(self.adjectives).title() + random.choice(self.nouns).title()
            if len(user) <= self.limit: break
        return user
