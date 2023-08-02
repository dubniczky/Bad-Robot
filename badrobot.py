import sys
import requests


def get_domain_rules(domain):
    res = requests.get(f'{domain}/robots.txt')
    if res.status_code == 200:
        return res.text
    return None


if __name__ == '__main__':
    if len(sys.argv < 2):
        print('')
        sys.exit(1)
    print(get_domain_rules(sys.argv[1]))