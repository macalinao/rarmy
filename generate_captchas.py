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
from rarmy.data import captchas

def main():
    """
    Main function of generate-captchas.
    """

    parser = ArgumentParser(description='Generates a series of CAPTCHA idens to \
        be evaluated manually. Future releases may automate captcha recognition.')
    parser.add_argument('--amount', default=1, type=int,
        help='The amount of CAPTCHAs desired.')

    args = parser.parse_args()

    idens = []
    print 'Generating ' + str(args.amount) + ' CAPTCHA idens per proxy.'

    d = 'output/'
    if not os.path.exists(d):
        print 'Directory "' + d + '" not found. Creating.'
        os.makedirs(d)

    idens_imgs = d + '/idens/'

    if not os.path.exists(idens_imgs):
        print 'Directory "' + idens_imgs + '" not found. Creating.'
        os.makedirs(idens_imgs)
    else:
        print 'Clearing idens imgs directory...'
        for f in os.listdir(idens_imgs):
            p = os.path.join(idens_imgs, f)
            try:
                os.unlink(p)
            except Exception, e:
                print e
        print 'Directory cleared.'

    for x in xrange(args.amount):
        iden = gen_iden()
        if not iden:
            continue
        print 'Generated iden ' + iden
        idens.append(iden)

    content = ''
    for i in idens:
        content += i[0:6] + '&nbsp;<img alt="' + i + '" title="' + i + '" src="idens/' + i + '.png" />'

    html = 'output/idens.html'
    d = os.path.dirname(html)
    if not os.path.exists(d):
        print 'Directory "' + d + '" not found. Creating.'
        os.makedirs(d)

    with open(html, 'w+') as outfile:
        outfile.write(content)
    print 'Open the HTML file ' + html + ' and input the CAPTCHA solutions below.'
    os.startfile(os.path.abspath(html))

    cs = []
    for iden in idens:
        sol = raw_input(iden + ': ').upper()
        cs.append([iden, sol])

    captchas.add(cs)
    print 'Saved CAPTCHAs to the CAPTCHA manager.'

def gen_iden():
    """
    Generates an iden.
    """
    captchas = []

    payload = {'id': 'login_reg', 'renderstyle': 'html'}
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}

    r = requests.post('http://www.reddit.com/api/new_captcha', data=urlencode(payload),
        headers=headers)

    try:
        iden = r.json()['jquery'][-1][-1][0]
    except:
        return None

    try:
        img = requests.get('http://www.reddit.com/captcha/' + iden + '.png', stream=True)
        with open('output/idens/' + iden + '.png', 'wb') as handle:
            for block in img.iter_content(1024):
                if not block:
                    break
                handle.write(block)

    except:
        return None
    return iden

if __name__ == "__main__":
    main()
