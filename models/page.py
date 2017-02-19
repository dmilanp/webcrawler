import logging

from bs4 import BeautifulSoup
from eventlet.green import urllib2
import validators


logging.getLogger(__name__)


class Page:

    FETCH_TIMEOUT_SECONDS = 4

    def __init__(self, url):
        self.url = self.ensure_url_protocol(url)
        self.resource = self.extract_resource_from_url(url)
        self._assets = []
        self._links = []
        self._html = None

    def has_valid_url(self):
        return self.is_valid_url(self.url)

    @staticmethod
    def ensure_url_protocol(url):
        """If protocol not provided fallback to http"""
        if not (url.startswith('https://') or url.startswith('http://')):
            logging.debug("Protocol not provided. Falling back to http.")
            return "http://" + url
        return url

    @staticmethod
    def is_valid_url(url):
        """Checks if url is valid"""
        if not validators.url(url):
            return False
        return True

    def extract_resource_from_url(self, url):
        raise NotImplementedError

    def __hash__(self):
        return self.url

    @property
    def internal_links(self):
        if not self._links:
            # compute links
            pass
        return self._links

    @property
    def assets(self):
        if not self._assets:
            # compute assets
            pass
        return self._assets

    def print_assets(self):
        raise NotImplementedError

    @property
    def html(self):
        # if retries_left == 0:
        #     logging.warning("Ran out of attempts for url {}".format(page.url))
        #     return
        # retries_left -= 1
        #
        # data = None
        # with eventlet.Timeout(FETCH_TIMEOUT_SECONDS, False):
        #     data = urllib2.urlopen(page.url).read()
        #
        # if not data:
        #     logging.warning("Fetching url {} timed out after {} seconds. Retrying.".format(page.url,
        #                                                                                    FETCH_TIMEOUT_SECONDS))
        #     pool.spawn_n(crawl, page, visited, pool, retries_left)
        # else:
        #     page.assets = extract_assets_from_html(data)
        #
        #
        #     for link in links:
        #         pool.spawn_n(crawl, link, visited, pool, MAX_RETRIES)
        return self._html


