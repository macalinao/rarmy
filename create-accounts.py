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
from lib.utils import namegen
import json
from time import sleep
import os

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
    parser.add_argument('--interval', default=610, type=float,
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
        captchas = parse_newline_file(args.captchas)
    except IOError:
        print 'Captchas file "' + args.captchas + '" does not exist!'
        return

    captchas = [ c.split('=') for c in captchas ]

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

    ng = namegen.Namegen(adjectives, nouns)

    accts = []
    for x in xrange(args.amount):
        if not captchas:
            print 'No more CAPTCHAs left!'
            break

        while True:
            if not captchas:
                print 'No more CAPTCHAs left!'
                break

            acct = {}

            acct['user'] = ng.generate()

            charset = string.ascii_lowercase + string.ascii_uppercase + string.digits
            acct['pass'] = ''.join(random.choice(charset) for i in xrange(10))

            captcha = captchas.pop()

            # Generate the request
            payload = {
                'op': 'reg',
                'user': acct['user'],
                'email': '',
                'passwd': acct['pass'],
                'passwd2': acct['pass'],
                'iden': captcha[0],
                'captcha': captcha[1],
                'rem': 'true',
                'api_type': 'json'
            }

            headers = {'Content-Type': 'application/x-www-form-urlencoded'}

            r = requests.post('https://ssl.reddit.com/api/register/' + acct['user'],
                data=urlencode(payload), headers=headers)

            json = r.json()
            if 'captcha' in json['json']:
                print 'Error in creating user ' + acct['user'] + ': ' + str(', '.join(e[0] for e in json['json']['errors']))
                continue

            print 'Account created: ' + str(acct)
            accts.append(acct)
            break

        if captchas:
            sleep(args.interval)

    output = args.output
    d = os.path.dirname(output)
    if not os.path.exists(d):
        print 'Directory "' + d + '" not found. Creating.'
        os.makedirs(d)

    with open(output, 'w+') as outfile:
        json.dump(accts, outfile, indent=4)
    print 'Done! ' + str(len(accts)) + ' generated accounts saved to file "' + args.output + '".'

def parse_newline_file(file):
    """
    Parses a newline-delimited file, given the file's name, returning
    each non-empty line with leading and trailing whitespace removed.
    """
    with open(file, 'r') as f:
        return [ l.strip() for l in f.read().split('\n') if l ]

if __name__ == "__main__":
    main()
