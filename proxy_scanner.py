from lib import proxies
import signal
import sys
import json
from argparse import ArgumentParser
import requests
from time import sleep
import os
from Queue import Queue
from threading import Thread

pl = []
output = ''
q = None

def main():
    """
    Main function of the proxy scanner.
    """
    global pl, output, q

    parser = ArgumentParser(description='Scans a list of proxies to determine which work for HTTPS.')
    parser.add_argument('--output', default='output/proxies.txt', type=str,
        help='The file in which to store the found proxies.')
    parser.add_argument('--threads', default=10, type=int,
        help='Number of threads to use.')

    args = parser.parse_args()
    output = args.output

    pm = proxies.ProxyManager()

    threads = args.threads
    q = Queue(threads * 3)

    print 'Starting threads.'
    for x in xrange(threads):
        t = Thread(target=check_proxies)
        t.daemon = True
        t.start()

    print 'Queueing proxies.'
    for proxy in pm.proxies:
        q.put(proxy)
    q.join()

    save_proxies()

def check_proxies():
    """
    Worker function that tests proxies.
    """
    while True:
        proxy = q.get()
        res = test_proxy('http://' + proxy)
        if res:
            pl.append(proxy)
            print 'GOOD ' + proxy

def test_proxy(proxy):
    """
    Tests a proxy.
    """
    try:
        r = requests.get('http://www.reddit.com/', proxies={'http': proxy}, timeout=3)
    except Exception, e:
        return False

    if not r.status_code < 400:
        return False

    if not 'Submit a new link' in r.text:
        return False

    return r.text

def save_proxies():
    """
    Saves all of our proxies.
    """
    global output, pl
    d = os.path.dirname(output)
    if not os.path.exists(d):
        print 'Directory "' + d + '" not found. Creating.'
        os.makedirs(d)

    with open(output, 'w+') as outfile:
        outfile.write('\n'.join(pl))
    print 'Done! ' + str(len(pl)) + ' confirmed proxies saved to file "' + output + '".'

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        save_proxies()
