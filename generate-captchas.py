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

def main():
    """
    Main function of generate-captchas.
    """

    parser = ArgumentParser(description='Generates a series of CAPTCHA idens to \
        be evaluated manually. Future releases may automate captcha recognition.')
    parser.add_argument('--amount', default=1, type=int,
        help='The amount of CAPTCHAs desired.')
    parser.add_argument('--output', default='output/idens.txt', type=str,
        help='The file in which to store the found idens in.')
    parser.add_argument('--html', default='output/idens.html', type=str,
        help='The file to create an HTML file at.')

    args = parser.parse_args()

    idens = []
    print 'Generating ' + str(args.amount) + ' CAPTCHA idens.'

    for x in xrange(args.amount):
        payload = {'id': 'login_reg', 'renderstyle': 'html'}
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}

        r = requests.post('http://www.reddit.com/api/new_captcha', data=urlencode(payload), headers=headers)
        iden = r.json()['jquery'][-1][-1][0]
        print 'Iden: ' + iden
        idens.append(iden)

        requests.get('http://www.reddit.com/captcha/' + iden + '.jpg')

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
        content += '<img src="http://www.reddit.com/captcha/' + i + '.png" />'

    html = args.html
    d = os.path.dirname(html)
    if not os.path.exists(d):
        print 'Directory "' + d + '" not found. Creating.'
        os.makedirs(d)

    with open(html, 'w+') as outfile:
        outfile.write(content)
    print 'HTML file successfully written to ' + html + '.'

if __name__ == "__main__":
    main()
