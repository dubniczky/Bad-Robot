#!/usr/bin/env python3

import sys
import re
import shutil
import os
import requests


TARGET_DIR = 'target'
REQUEST_TIMEOUT = 5
SUBFOLDER_REPLACE = '--'


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
            print(f'[+] {url}')
            with open(f'{local}/{path.replace("/", SUBFOLDER_REPLACE).strip("-")}', 'w', encoding='utf8') as f:
                f.write(res.text)
        else:
            print(f'[-] {url} returned {res.status_code}')


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