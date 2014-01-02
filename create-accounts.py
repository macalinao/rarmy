#!/usr/bin/env python

"""
Creates accounts from CAPTCHA solutions, using a
wordbank to generate realistic-sounding usernames.
"""

from argparse import ArgumentParser

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

if __name__ == "__main__":
    main()
