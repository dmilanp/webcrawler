import logging
import re
from urlparse import urlparse

from bs4 import BeautifulSoup
import eventlet
from eventlet.green import urllib2
import validators


logging.getLogger(__name__)


class Page:

    FETCH_TIMEOUT_SECONDS = 4
    MAX_RETRIES = 3

    def __init__(self, url):
        self.url = self.ensure_url_protocol(url)
        self.path = self.extract_path_from_url(url)
        self._assets = []
        self._links = []
        self._html = None
        self.retries = Page.MAX_RETRIES

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

    @staticmethod
    def extract_path_from_url(url):
        return urlparse(url).path

    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url

    @property
    def internal_links(self):

        if not self._links:
            # Get links
            soup = BeautifulSoup(self.html, 'html.parser')
            domain = urlparse(self.url).netloc
            anchors = soup.find_all('a', href=re.compile(domain))
            links = filter(None, map(lambda anchor: anchor.href, anchors))
            self._links = links
        return self._links

    @property
    def assets(self):
        if not self._assets:

            def is_asset(tag):
                return tag.name in ['a', 'link', 'img', 'script']

            def get_asset_link(tag):
                if tag.name == "a":
                    return tag.href
                elif tag.name == "link":
                    return tag.rel
                elif tag.name == "img" or tag.name == "script":
                    return tag.src
                else:
                    logging.warning("Couldn't get asset for {}".format(tag))

            # Get assets
            soup = BeautifulSoup(self.html, 'html.parser')
            assets = soup.find_all(is_asset)
            asset_links = filter(None, map(get_asset_link, assets))
            self._links = asset_links
        return self._assets

    def print_assets(self):
        raise NotImplementedError

    @property
    def html(self):
        if not self._html:
            # Adhere to number of retries specified
            if self.retries == 0:
                logging.warning("Ran out of attempts for url {}".format(self.url))
                self._html = ""
            else:
                self.retries -= 1
                data = None
                with eventlet.Timeout(Page.FETCH_TIMEOUT_SECONDS):
                    data = urllib2.urlopen(self.url).read()

                if data:
                    self._html = data
                else:
                    self._html = ""

        return self._html


