# -*- coding: utf-8 -*-
import logging
from urlparse import urlparse
import re

from bs4 import BeautifulSoup
import eventlet
from eventlet.green import urllib2

from models.helpers import ensure_url_protocol, extract_path_from_url, domain_for_url, is_valid_url

logging.getLogger(__name__)


class Page:

    FETCH_TIMEOUT_SECONDS = 5
    MAX_RETRIES = 3

    def __init__(self, url):
        self.url = ensure_url_protocol(url)
        self.path = extract_path_from_url(url)
        self.domain = domain_for_url(self.url)
        self._assets = None
        self._internal_links = None
        self._html = None
        self.retries_left = Page.MAX_RETRIES

    def __hash__(self):
        """The uniqueness of a page is defined by its url"""
        return hash(self.url)

    def __eq__(self, other):
        return self.url == other.url

    @property
    def has_valid_url(self):
        return is_valid_url(self.url)

    def print_assets(self):
        """Prints links embedded in the following tags in its html: a, img, script, link"""
        print '\n', 'Assets for {} :'.format(self.url)
        for asset in sorted(list(self.extract_assets)):
            print '\t', asset
        print '\n'

    def extract_internal_link(self, link):
        """If link is to same domain this returns it well formatted, otherwise returns None"""
        if self.domain in link and 'mailto' not in link:
            # Guard cases like https://plus.google.com/share?url=http%3A%2F%2Fwww.headspace.com

            if not self.domain == Page(link).domain:
                return None

            link = ensure_url_protocol(link)

            # Clean multiple slashes
            output = re.sub('http://[/]+', 'http://', link)
            return output

        # References to resource only
        elif not link.startswith('http') and not link.startswith('www') and re.match('[/.a-zA-Z0-9-]*', link) \
                and 'mailto:' not in link and 'tel:' not in link:
            link = link.replace('../', '')
            link = re.sub('^/', '', link)
            return ensure_url_protocol(urlparse(self.url).netloc) + '/' + link
        else:
            return None

    def extract_internal_links(self):
        """Prints links to pages in same domain as self"""
        if not self._internal_links:
            soup = BeautifulSoup(self.get_html(), 'html.parser')
            anchors = soup.find_all('a')
            internal_links = set()

            for anchor in anchors:
                href = anchor.get('href')
                internal_link = self.extract_internal_link(href)
                internal_link_with_protocol = ensure_url_protocol(internal_link)
                internal_links.add(internal_link_with_protocol)

            self._internal_links = internal_links

        return self._internal_links

    def extract_assets(self):
        """Prints links embedded in its following tags: a, img, script, link"""
        if not self._assets:
            def is_asset(tag):
                return tag.name in ['a', 'link', 'img', 'script']

            def get_asset_link(tag):
                if tag.name == 'a' or tag.name == 'link':
                    return tag.get('href')
                elif tag.name == 'img' or tag.name == 'script':
                    return tag.get('src')

            def prepare_asset(asset):
                if asset.startswith('www'):
                    return ensure_url_protocol(asset)
                elif asset.startswith('http'):
                    return asset
                elif asset.startswith('/'):
                    asset = re.sub('^/', '', asset)
                return '{}/{}'.format(self.url, asset)

            # Extract assets
            soup = BeautifulSoup(self.get_html(), 'html.parser')
            assets = soup.find_all(is_asset)
            asset_links = filter(None, map(get_asset_link, assets))
            cleaned = map(lambda l: l.replace('../', ''), asset_links)
            cleaned = map(lambda l: re.sub('^//', '/', l), cleaned)
            output = filter(lambda l: not l.startswith('?') and not l.startswith('#'), cleaned)
            formatted_output = map(prepare_asset, output)
            self._assets = set(formatted_output)

        return self._assets

    def get_html(self):
        """Fetches html contents of self.url"""
        if not self._html:
            data = ''

            with eventlet.Timeout(Page.FETCH_TIMEOUT_SECONDS):
                try:
                    data = urllib2.urlopen(self.url).read()
                except urllib2.HTTPError:
                    logging.debug('HTTP request failed for url {}'.format(self.url))
                except eventlet.Timeout as t:
                    logging.debug('Timeout crawling {}. Retrying.'.format(self.url))
                    raise t
                except urllib2.URLError:
                    logging.debug('Error opening URL {}'.format(self.url))
                except:
                    pass

            self._html = data

        return self._html



