# -*- coding: utf-8 -*-
import argparse
import logging
import sys
import time
import random

import eventlet

from models.page import Page


parser = argparse.ArgumentParser(description='This script takes a url to crawl and outputs its site\'s map and a full '
                                             'list of its assets.')
parser.add_argument('url', type=str, help='url to crawl')
parser.add_argument('--max-threads', '-mt', type=int, default=10, help='maximum number of threads to perform crawling')
parser.add_argument('--soft', action="store_true", default=False, help='sleep a fraction of a second before crawling a '
                                                                       'new page')
args = parser.parse_args()

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

url = args.url
max_threads = args.max_threads
soft = args.soft


def print_sitemap(url, pages):
    print '\n', 'Sitemap for {} :'.format(url)
    for page in pages:
        print '\t', page.path


def crawl(page, visited, pool):
    """Crawl url, build site's map and list assets"""
    logging.info('Crawling {}'.format(page.url))
    visited.add(page)
    if soft:
        time.sleep(random.random())

    try:
        links = page.extract_internal_links()
    except eventlet.Timeout:
        page.retries_left -= 1
        if page.retries_left > 0:
            pool.spawn_n(crawl, page, visited, pool)
        else:
            logging.warning('Couldn\'t fetch {} after {} retries.'.format(page.url, Page.MAX_RETRIES))
        return

    for link in links:
        new_page = Page(link)
        if new_page not in visited:
            pool.spawn_n(crawl, new_page, visited, pool)
        else:
            # Url already crawled
            pass

    page.print_assets()


if __name__ == '__main__':

    if soft:
        logging.info('Soft mode enabled.')
    logging.info('Using pool of {} threads.'.format(max_threads))

    root_page = Page(url)
    if not root_page.has_valid_url:
        logging.error('Url {} is not valid'.format(root_page.url))
        exit(1)

    visited = set()
    pool = eventlet.GreenPool(size=max_threads)
    crawl(root_page, visited, pool)
    pool.waitall()

    print '\n', 'Sitemap for {} :'.format(root_page.url)
    for page in sorted(list(visited)):
        if page.path:
            print '\t', page.path
