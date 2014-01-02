#!/usr/bin/env python

"""
Creates accounts from CAPTCHA solutions, using a
wordbank to generate realistic-sounding usernames.
"""

from urllib import urlencode
from argparse import ArgumentParser
import random
import string
import requests

def main():
    """
    Main function of create-accounts.
    """
    parser = ArgumentParser(description='Creates accounts from CAPTCHA solutions, \
        using a wordbank to generate realistic-sounding usernames.')
    parser.add_argument('--amount', default=1, type=int,
        help='The amount of accounts desired.')
    parser.add_argument('--tor', default=True, type=bool,
        help='Enable this flag to use Tor. You can only generate one account every 10 minutes if this is not enabled.')
    parser.add_argument('--interval', default=610, type=str,
        help='The interval in which accounts are created in seconds.')

    # Typical users should leave these alone
    parser.add_argument('--captchas', default='output/captchas.txt', type=str,
        help='The file containing the idens and solved captchas, delimited by an equals sign and newlines.')
    parser.add_argument('--output', default='output/accounts.json', type=str,
        help='The file in which to store information of the generated accounts in.')
    parser.add_argument('--adjectives', default='txt/adjectives.txt', type=str,
        help='The file containing an adjective list.')
    parser.add_argument('--nouns', default='txt/nouns.txt', type=str,
        help='The file containing a noun list.')

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
            acct['user'] = random.choice(adjectives).title() + random.choice(nouns).title()
            invalid = len(acct['user']) > 20
        
        charset = string.ascii_lowercase + string.ascii_uppercase + string.digits
        acct['pass'] = ''.join(random.choice(charset) for i in xrange(10))

        # Generate the request
        payload = {
            'op': 'reg',
            'user': acct['user'],
            'email': '',
            'passwd': acct['pass'],
            'passwd2': acct['pass'],
            'iden': '...',
            'captcha': '...',
            'rem': 'true',
            'api_type': 'json'
        }

        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        r = requests.post('https://ssl.reddit.com/api/register/' + acct['user'],
            data=urlencode(payload), headers=headers)

        if 'captcha' in r.text:
            print 'error'
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
