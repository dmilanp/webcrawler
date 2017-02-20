# -*- coding: utf-8 -*-
import logging
from urlparse import urlparse
import re

from bs4 import BeautifulSoup
import tldextract
import eventlet
from eventlet.green import urllib2
import validators


logging.getLogger(__name__)


class Page:

    FETCH_TIMEOUT_SECONDS = 5
    MAX_RETRIES = 3

    def __init__(self, url):
        # Always store url with scheme
        self.url = self.ensure_url_protocol(url)
        self.path = self.extract_path_from_url(url)
        self.domain = self.domain_for(self.url)
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
        for asset in sorted(list(self.get_assets)):
            print "\t", asset
        print "\n"

    def extract_internal_link(self, link):
        """If link is to same domain this returns it well formatted, otherwise returns None"""
        # Links containing domain
        if self.domain in link and "mailto" not in link:
            # Guard cases like https://plus.google.com/share?url=http%3A%2F%2Fwww.headspace.com
            if not self.domain == Page(link).domain:
                return None
            link = Page.ensure_url_protocol(link)
            # Clean multiple slashes
            output = re.sub("http://[/]+", "http://", link)
            return output
        # References to resource only
        elif not link.startswith("http") and not link.startswith("www") and re.match("[/.a-zA-Z0-9-]*", link) \
                and "mailto:" not in link and "tel:" not in link:
            link = link.replace('../', '')
            link = re.sub("^/", "", link)
            return Page.ensure_url_protocol(urlparse(self.url).netloc) + "/" + link
        else:
            return None

    @property
    def get_internal_links(self):
        """Prints links to pages in same domain as self"""
        if not self._links:
            # Extract links
            soup = BeautifulSoup(self.html, 'html.parser')
            anchors = soup.find_all('a')
            href = filter(None, map(lambda tag: tag.get('href'), anchors))
            internal_links = filter(None, map(self.extract_internal_link, href))
            # Work with fully qualified links, with scheme
            links = map(Page.ensure_url_protocol, internal_links)
            # Clean paths
            output = map(lambda l: urlparse(l).scheme + "://" + urlparse(l).netloc + Page.extract_path_from_url(l),
                         links)
            self._links = set(output)
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
            cleaned = map(lambda l: l.replace('../', ''), asset_links)
            cleaned = map(lambda l: re.sub('^//', '/', l), cleaned)
            output = filter(lambda l: not l.startswith('?') and not l.startswith('#'), cleaned)
            formatted_output = map(lambda l: l if (l.startswith('/') or l.startswith("http") or
                                                   l.startswith("www")) else "/{}".format(l),
                                   output)
            self._assets = set(formatted_output)
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
                    logging.debug("Timeout crawling {}. Retrying.".format(self.url))
                    raise t
                except urllib2.URLError:
                    logging.debug("Error opening URL {}".format(self.url))
                except:
                    pass
            self._html = data
        return self._html

    @staticmethod
    def domain_for(url):
        tld = tldextract.extract(url)
        return "{}.{}".format(tld.domain, tld.suffix)

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

