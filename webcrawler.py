import argparse
import logging
import sys

import validators


parser = argparse.ArgumentParser(description='This script takes a url to crawl and outputs its site\'s map and a full '
                                             'list of its assets.')
parser.add_argument('url', type=str, help='url to crawl')
args = parser.parse_args()

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def validate_url(url):
    if not validators.url(url):
        logging.error("URL provided ({}) is not valid.".format(url))
        exit(1)


def crawl(url):
    pass


if __name__ == '__main__':
    url = args.url
    validate_url(url)
    crawl(url)
