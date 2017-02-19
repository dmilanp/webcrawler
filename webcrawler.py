import argparse
import logging
import sys

import eventlet
from eventlet.green import urllib2
import validators


parser = argparse.ArgumentParser(description='This script takes a url to crawl and outputs its site\'s map and a full '
                                             'list of its assets.')
parser.add_argument('url', type=str, help='url to crawl')
parser.add_argument('--max-threads', '-mt', type=int, default=10, help='maximum number of threads to perform crawling')
args = parser.parse_args()

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

RETRIES = 1
FETCH_TIMEOUT_SECONDS = 4

def ensure_protocol_in_url(url):
    """If protocol not provided fallback to http"""
    if not (url.startswith('https://') or url.startswith('http://')):
        logging.debug("Protocol not provided. Falling back to http.")
        return "http://" + url
    return url


def validate_url(url):
    """Check if url is valid, exit otherwise"""
    if not validators.url(url):
        logging.error("URL provided ({}) is not valid.".format(url))
        exit(1)


def crawl(url, visited, pool, retries_left):
    """Crawl url, build site's map and list its assets"""
    logging.debug("Crawling {}".format(url))

    if retries_left == 0:
        logging.warning("Ran out of attempts for url {}".format(url))
        return
    retries_left -= 1

    data = None
    with eventlet.Timeout(FETCH_TIMEOUT_SECONDS, False):
        data = urllib2.urlopen(url).read()
    if not data:
        logging.warning("Fetching url {} timed out after {} seconds. Retrying.".format(url, FETCH_TIMEOUT_SECONDS))
        pool.spawn_n(crawl, url, visited, pool, retries_left)
    else:
        logging.debug(data)


if __name__ == '__main__':
    # Get url and validate
    url = args.url
    max_threads = args.max_threads
    url = ensure_protocol_in_url(url)
    validate_url(url)

    # Perform crawling
    visited = set()
    pool = eventlet.GreenPool(size=max_threads)
    crawl(url, visited, pool, RETRIES)
    pool.waitall()
