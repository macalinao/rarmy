#!/usr/bin/env python

"""
Creates accounts from CAPTCHA solutions, using a
wordbank to generate realistic-sounding usernames.
"""

from argparse import ArgumentParser
import random
import string

def main():
    """
    Main function of create-accounts.
    """
    parser = ArgumentParser(description='Creates accounts from CAPTCHA solutions, \
        using a wordbank to generate realistic-sounding usernames.')
    parser.add_argument('--amount', default=1, type=int,
        help='The amount of accounts desired.')
    parser.add_argument('--output', default='output/accounts.json', type=str,
        help='The file in which to store information of the generated accounts in.')
    parser.add_argument('--adjectives', default='txt/adjectives.txt', type=str,
        help='The file containing an adjective list.')
    parser.add_argument('--nouns', default='txt/nouns.txt', type=str,
        help='The file containing a noun list.')
    parser.add_argument('--captchas', default='output/captchas.txt', type=str,
        help='The file containing the idens and solved captchas, delimited by an equals sign and newlines.')

    args = parser.parse_args()

    try:
        adjectives = parse_newline_file(args.adjectives)
    except IOError:
        print 'Adjectives file "' + args.adjectives + '" does not exist!'
        return

    try:
        nouns = parse_newline_file(args.nouns)
    except IOError:
        print 'Nouns file "' + args.nouns + '" does not exist!'
        return

    accts = []
    for x in xrange(args.amount):
        acct = {}

        invalid = True
        while invalid:
            acct['name'] = random.choice(adjectives).title() + random.choice(nouns).title()
            invalid = len(acct['name']) > 20
        
        charset = string.ascii_lowercase + string.ascii_uppercase + string.digits
        acct['pass'] = ''.join(random.choice(charset) for i in xrange(10))

        print 'Account created: ' + str(acct)

def parse_newline_file(file):
    """
    Parses a newline-delimited file, given the file's name, returning
    each non-empty line with leading and trailing whitespace removed.
    """
    with open(file, 'r') as f:
        return [ l.strip() for l in f.read().split('\n') if l ]

if __name__ == "__main__":
    main()
