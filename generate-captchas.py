#!/usr/bin/env python

"""
Generates a series of CAPTCHA idens to be evaluated
manually. Future releases may automate captcha recognition.
"""

import os
import requests
from argparse import ArgumentParser
from urllib import urlencode
from time import sleep
from lib import dbs

def main():
    """
    Main function of generate-captchas.
    """

    parser = ArgumentParser(description='Generates a series of CAPTCHA idens to \
        be evaluated manually. Future releases may automate captcha recognition.')
    parser.add_argument('--amount', default=1, type=int,
        help='The amount of CAPTCHAs desired. This amount is per proxy.')
    parser.add_argument('--no-proxies', action='store_false', dest='proxies',
        help='Disables proxies.')
    parser.set_defaults(proxies=True)
    parser.add_argument('--output', default='output/idens.txt', type=str,
        help='The file in which to store the found idens in.')
    parser.add_argument('--html', default='output/idens.html', type=str,
        help='The file to create an HTML file at.')

    args = parser.parse_args()

    idens = []
    print 'Generating ' + str(args.amount) + ' CAPTCHA idens per proxy.'

    if args.proxies:
        proxies = dbs.load_proxies()
    else:
        proxies = [None]

    for proxy in proxies:
        for x in xrange(args.amount):
            iden = gen_iden(proxy)
            print 'Generated iden ' + iden[0] + ' with proxy ' + iden[1]
            idens.append('='.join(iden))

    output = args.output
    d = os.path.dirname(output)
    if not os.path.exists(d):
        print 'Directory "' + d + '" not found. Creating.'
        os.makedirs(d)

    with open(output, 'w+') as outfile:
        outfile.write('\n'.join(idens))
    print 'Idens successfully written to ' + output + '.'

    content = ''
    for i in idens:
        content += '<img src="http://www.reddit.com/captcha/' + i[0] + '.png" />'

    html = args.html
    d = os.path.dirname(html)
    if not os.path.exists(d):
        print 'Directory "' + d + '" not found. Creating.'
        os.makedirs(d)

    with open(html, 'w+') as outfile:
        outfile.write(content)
    print 'HTML file successfully written to ' + html + '.'

def gen_iden(proxy=None):
    """
    Generates an iden for the given proxy. Set proxy to None to not generate
    on a proxy.
    """
    captchas = []

    payload = {'id': 'login_reg', 'renderstyle': 'html'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    proxies = {'http': proxy} if proxy else {}

    r = requests.post('http://www.reddit.com/api/new_captcha', data=urlencode(payload),
        headers=headers, proxies=proxies)
    iden = r.json()['jquery'][-1][-1][0]
    proxy_str = proxy if proxy else 'none'

    requests.get('http://www.reddit.com/captcha/' + iden[0] + '.png', proxies=proxies)
    return [iden, proxy_str]

if __name__ == "__main__":
    main()
