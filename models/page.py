import logging
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
        self._assets = None
        self._links = None
        self._html = None
        self.retries_left = Page.MAX_RETRIES

    def __hash__(self):
        """The uniqueness of a page is defined by its url"""
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url



    def has_valid_url(self):
        return self.is_valid_url(self.url)

    def print_assets(self):
        """Prints links embedded in the following tags in its html: a, img, script, link"""
        print "\n", "Assets for {} :".format(self.url)
        for asset in self.get_assets:
            print "\t", asset

    @property
    def get_internal_links(self):
        """Prints links to pages in same domain as self"""
        if not self._links:
            def get_internal_link(tag):
                link = tag.get('href')
                if link:
                    if urlparse(self.url).netloc in link:
                        return link
                    elif not self.is_valid_url(link):
                        return urlparse(self.url).netloc + "/" + link
                else:
                    return None

            # Extract links
            soup = BeautifulSoup(self.html, 'html.parser')
            anchors = soup.find_all('a')
            links = filter(None, map(get_internal_link, anchors))
            self._links = set(links)
        return self._links

    @property
    def get_assets(self):
        """Prints links embedded in its following tags: a, img, script, link"""
        if not self._assets:
            def is_asset(tag):
                return tag.name in ['a', 'link', 'img', 'script']

            def get_asset_link(tag):
                if tag.name == "a" or tag.name == "link":
                    return tag.get('href')
                elif tag.name == "img" or tag.name == "script":
                    return tag.get('src')

            # Extract assets
            soup = BeautifulSoup(self.html, 'html.parser')
            assets = soup.find_all(is_asset)
            asset_links = filter(None, map(get_asset_link, assets))
            self._assets = set(asset_links)
        return self._assets

    @property
    def html(self):
        """Fetches html contents of self.url"""
        if not self._html:
            data = ""
            with eventlet.Timeout(Page.FETCH_TIMEOUT_SECONDS):
                try:
                    data = urllib2.urlopen(self.url).read()
                except urllib2.HTTPError:
                    logging.debug("HTTP request failed for url {}".format(self.url))
                except eventlet.Timeout as t:
                    logging.debug("Raising timeout from page")
                    raise t
            self._html = data
        return self._html

    @staticmethod
    def is_valid_url(url):
        """Checks if url is valid"""
        if not validators.url(Page.ensure_url_protocol(url)):
            return False
        return True

    @staticmethod
    def ensure_url_protocol(url):
        """If protocol not provided fallback to http"""
        if not (url.startswith('https://') or url.startswith('http://')):
            return "http://" + url
        return url

    @staticmethod
    def extract_path_from_url(url):
        """Returns resource part of url without domain"""
        return urlparse(Page.ensure_url_protocol(url)).path

