#!/usr/bin/env python3

import sys
import re
import shutil
import os
import requests


TARGET_DIR = 'target'
REQUEST_TIMEOUT = 5
SUBFOLDER_REPLACE = '--'


class colors:
    # Special
    reset      = '\033[0m'
    # Foreground
    black      = '\033[30m'
    blue       = '\033[34m'
    cyan       = '\033[36m'
    darkgrey   = '\033[90m'
    green      = '\033[32m'
    lightblue  = '\033[94m'
    lightcyan  = '\033[96m'
    lightgreen = '\033[92m'
    lightgrey  = '\033[37m'
    lightred   = '\033[91m'
    orange     = '\033[33m'
    pink       = '\033[95m'
    purple     = '\033[35m'
    red        = '\033[31m'
    yellow     = '\033[93m'
    

def color(text, color):
    return color + str(text) + colors.reset


def get_domain_rules(domain):
    res = requests.get(f'{domain}/robots.txt', timeout=REQUEST_TIMEOUT)
    if res.status_code == 200:
        return res.text
    return None


def filter_disallow_rules(rules):
    disallows = []
    for rule in rules:
        if rule.startswith('Disallow: '):
            disallows.append(rule.split(': ')[1])
    return disallows


def filter_paths(paths, filters):
    res = paths[:]
    for f in filters:
        res = list(filter(lambda p, filt=f: not re.search(filt, p), res))
    return res


def clean_target(path):
    os.makedirs(path, exist_ok=True)
    shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
    

def download_paths(domain, paths, local):
    for path in paths:
        url = f'{domain}{path}'
        res = requests.get(url, timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            print(f'[ {color(res.status_code, colors.green)} ] {url}')
            with open(f'{local}/{path.replace("/", SUBFOLDER_REPLACE).strip("-")}', 'w', encoding='utf8') as f:
                f.write(res.text)
        else:
            print(f'[ {color(res.status_code, colors.red)} ] {url}')


def main():
    if len(sys.argv) < 2:
        print('Usage: python badrobot.py <domain>')
        print('Example: python badrobot.py https://example.com')
        sys.exit(1)
        
    # Download robots.txt
    domain = sys.argv[1]
    rule_file = get_domain_rules(domain)
    if rule_file is None:
        print(f'No robots.txt found at {domain}/robots.txt')
        sys.exit(1)
    print(f'Found robots.txt at {domain}/robots.txt')
    
    # Filter relevant rules
    disallows = filter_disallow_rules(rule_file.splitlines())
    filters = [
        r'[*]', # * is used for generalization, not a file
        r'[=]', # = is used for paths with specific arguments
    ]
    disallows = filter_paths(disallows, filters)
    print(f'Found robots.txt at {domain}/robots.txt')
    
    # Prepare target directory
    clean_target(TARGET_DIR)
    with open(f'{TARGET_DIR}/robots.txt', 'w', encoding='utf8') as f:
        f.write(rule_file)
        
    download_paths(domain, disallows, TARGET_DIR)




if __name__ == '__main__':
    main()
