import argparse
import logging
import sys

import validators


parser = argparse.ArgumentParser(description='This script takes a url to crawl and outputs its site\'s map and a full '
                                             'list of its assets.')
parser.add_argument('url', type=str, help='url to crawl')
args = parser.parse_args()

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def ensure_protocol(url):
    """If protocol not provided fallback to http"""
    if not (url.startswith('https://') or url.startswith('http://')):
        logging.debug("Protocol not provided. Falling back to http.")
        url = "http://" + url
    return url


def validate_url(url):
    """Check if url is valid, exit otherwise"""
    if not validators.url(url):
        logging.error("URL provided ({}) is not valid.".format(url))
        exit(1)


def crawl(url):
    """Crawl url, build site's map and list its assets"""
    logging.debug("Crawling {}".format(url))


if __name__ == '__main__':
    url = args.url
    url = ensure_protocol(url)
    validate_url(url)
    crawl(url)
