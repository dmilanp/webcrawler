import argparse

parser = argparse.ArgumentParser(description='This script takes a url to crawl and outputs its site\'s map and a full'
                                             'list of its assets.')
parser.add_argument('url', type=str, help='url to crawl')
args = parser.parse_args()

def validate_url(url):
    pass

def crawl(url):
    pass

if __name__ == '__main__':
    url = args.url
    validate_url(url)
    crawl(url)