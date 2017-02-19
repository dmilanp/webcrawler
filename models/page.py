import logging

from bs4 import BeautifulSoup
from eventlet.green import urllib2
import validators


logging.getLogger(__name__)


class Page:

    FETCH_TIMEOUT_SECONDS = 4

    def __init__(self, url):
        self.url = url
        self.resource = self.extract_resource_from_url(url)
        self._assets = []
        self._links = []
        self._html = None

    def has_valid_url(self):
        return self.validate_url(self.url)

    @staticmethod
    def ensure_url_protocol(url):
        """If protocol not provided fallback to http"""
        if not (url.startswith('https://') or url.startswith('http://')):
            logging.debug("Protocol not provided. Falling back to http.")
            return "http://" + url
        return url

    @staticmethod
    def validate_url(url):
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
        return self._html


