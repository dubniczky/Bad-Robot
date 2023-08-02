import sys
import re
import shutil
import os
import requests


TARGET_DIR = 'target'


def get_domain_rules(domain):
    res = requests.get(f'{domain}/robots.txt')
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
        res = list(filter(lambda p: not re.search(f, p), res))
    return res


def clean_target(path):
    os.makedirs(path, exist_ok=True)
    shutil.rmtree(path)
    os.makedirs(path, exist_ok=True)
    

def download_paths(domain, paths, local):
    for path in paths:
        url = f'{domain}{path}'
        res = requests.get(url)
        if res.status_code == 200:
            print(f'[+] Found {url}')
            with open(f'{local}/{path.replace("/", "--").strip("-")}', 'w', encoding='utf8') as f:
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
    
    # Filter relevant rules
    disallows = filter_disallow_rules(rule_file.splitlines())
    filters = [
        r'[*]', # * is used for generalization, not a file
        r'[=]', # = is used for paths with specific arguments
    ]
    disallows = filter_paths(disallows, filters)
    
    # Prepare target directory
    clean_target(TARGET_DIR)
    with open(f'{TARGET_DIR}/robots.txt', 'w', encoding='utf8') as f:
        f.write(rule_file)
        
    download_paths(domain, disallows, TARGET_DIR)
    
    


if __name__ == '__main__':
    main()