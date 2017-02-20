import argparse
import logging
import sys

import eventlet

from models.page import Page


parser = argparse.ArgumentParser(description='This script takes a url to crawl and outputs its site\'s map and a full '
                                             'list of its assets.')
parser.add_argument('url', type=str, help='url to crawl')
parser.add_argument('--max-threads', '-mt', type=int, default=10, help='maximum number of threads to perform crawling')
args = parser.parse_args()

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def print_sitemap(pages):
    raise NotImplementedError


def crawl(page, visited, pool):
    """Crawl url, build site's map and list its assets"""
    logging.debug("Crawling {}".format(page.url))

    try:
        links = page.internal_links
    except eventlet.Timeout:
        logging.warning("Fetching url {} timed out after {} seconds. Retrying.".format(page.url,
                                                                                       Page.FETCH_TIMEOUT_SECONDS))
        page.retries -= 1
        pool.spawn_n(crawl, page, visited, pool)
        return

    for link in links:
        new_page = Page(link)
        if new_page not in visited:
            pool.spawn_n(crawl, new_page, visited, pool)

    visited.add(page)


if __name__ == '__main__':
    # Get arguments
    url = args.url
    max_threads = args.max_threads

    # Set root URL
    root_page = Page(url)
    if not root_page.has_valid_url():
        logging.error("Url {} is not valid".format(root_page.url))
        exit(1)

    # Perform crawling
    visited = set()
    pool = eventlet.GreenPool(size=max_threads)
    crawl(root_page, visited, pool)
    pool.waitall()

    print_sitemap(visited)

    for page in visited:
        page.print_assets

