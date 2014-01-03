import json

def parse_newline_file(file):
    """
    Parses a newline-delimited file, given the file's name, returning
    each non-empty line with leading and trailing whitespace removed.
    """
    with open(file, 'r') as f:
        return [ l.strip() for l in f.read().split('\n') if l ]

def try_parse_newline_file(file):
    try:
        return parse_newline_file(file)
    except IOError:
        print 'File ' + file + ' does not exist!'
        return []

def load_proxies():
    """
    Loads proxies.
    """
    return try_parse_newline_file('config/proxies.txt')

def load_adjectives():
    """
    Loads adjectives.
    """
    return try_parse_newline_file('txt/adjectives.txt')

def load_nouns():
    """
    Loads nouns.
    """
    return try_parse_newline_file('txt/nouns.txt')

def load_useragents():
    """
    Loads useragents.
    """
    return try_parse_newline_file('txt/useragents.txt')

def load_accts():
    """
    Loads accts.
    """
    try:
        with open('config/accounts.json', 'r') as f:
            return json.load(f)
    except IOError:
        print 'Accounts file could not be loaded!'
        return []

def load_captchas():
    """
    Loads the captchas file.
    """
    lines = try_parse_newline_file('output/captchas.txt')
    return [ c.split('=') for c in lines ]
