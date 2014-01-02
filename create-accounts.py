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
from lib import dbs
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
    parser.add_argument('--interval', default=600, type=float,
        help='The interval in which accounts are created in seconds, per proxy.')
    parser.add_argument('--output', default='output/accounts.json', type=str,
        help='The file in which to store information of the generated accounts in.')

    args = parser.parse_args()

    captchas = dbs.load_captchas()
    ng = namegen.Namegen()

    accts = []
    for c in captchas:
        res = gen_acct(ng.generate(), c)

        if 'errors' in res:
            print ', '.join(e[0] for e in res['errors'])
            continue

        acct = res['acct']
        print 'Account created: ' + str(acct)
        accts.push(acct)

        if len(accts) > args.amount:
            break

    output = args.output
    d = os.path.dirname(output)
    if not os.path.exists(d):
        print 'Directory "' + d + '" not found. Creating.'
        os.makedirs(d)

    with open(output, 'w+') as outfile:
        json.dump(accts, outfile, indent=4)
    print 'Done! ' + str(len(accts)) + ' generated accounts saved to file "' + args.output + '".'

def gen_acct(user, captcha):
    [iden, proxy, sol] = captcha
    acct = {}

    acct['user'] = user

    charset = string.ascii_lowercase + string.ascii_uppercase + string.digits
    acct['pass'] = ''.join(random.choice(charset) for i in xrange(10))

    ret = {'acct': acct}

    # Generate the request
    payload = {
        'op': 'reg',
        'user': acct['user'],
        'email': '',
        'passwd': acct['pass'],
        'passwd2': acct['pass'],
        'iden': iden,
        'captcha': sol,
        'rem': 'true',
        'api_type': 'json'
    }

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post('https://ssl.reddit.com/api/register/' + acct['user'],
        data=urlencode(payload), headers=headers, proxies=({'http': proxy} if not proxy is 'none' else {}))
    print r.text

    rdata = r.json()
    if 'captcha' in rdata['json']:
        ret['errors'] = rdata['json']['errors']

    return ret

if __name__ == "__main__":
    main()
