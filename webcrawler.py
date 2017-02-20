import argparse
import logging
import sys
import time

import eventlet

from models.page import Page


parser = argparse.ArgumentParser(description='This script takes a url to crawl and outputs its site\'s map and a full '
                                             'list of its assets.')
parser.add_argument('url', type=str, help='url to crawl')
parser.add_argument('--max-threads', '-mt', type=int, default=10, help='maximum number of threads to perform crawling')
args = parser.parse_args()

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


def print_sitemap(root_page, pages):
    print "\nSitemap for {} :".format(root_page.url)
    for page in pages:
        print page.path


def crawl(page, visited, pool):
    """Crawl url, build site's map and list its assets"""
    try:
        links = page.internal_links
    except eventlet.Timeout:
        logging.warning("Timeout for url {} after {} seconds. Retrying.".format(page.url, Page.FETCH_TIMEOUT_SECONDS))
        logging.warning("{} retries left for url {}.".format(page.retries, page.url))
        page.retries -= 1
        if page.retries > 0:
            pool.spawn_n(crawl, page, visited, pool)
        return

    visited.add(page)

    for link in links:
        # time.sleep(1)
        new_page = Page(link)
        if new_page not in visited:
            pool.spawn_n(crawl, new_page, visited, pool)
        else:
            # logging.debug("Url {} already crawled. Skipping.".format(new_page.url))
            pass

    page.print_assets()

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

    print_sitemap(root_page, sorted(list(visited)))

    # for page in visited:
    #     page.print_assets()

