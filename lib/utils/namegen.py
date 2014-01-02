#!/usr/bin/env python

import random

class Namegen(object):
    """
    Generates random account usernames.
    """
    def __init__(self, adjectives, nouns, limit=20):
        self.adjectives = adjectives
        self.nouns = nouns
        self.limit = limit

    def generate(self):
        """
        Generates the account name.
        """
        while True:
            user = random.choice(self.adjectives).title() + random.choice(self.nouns).title()
            if len(user) <= self.limit: break
        return user
