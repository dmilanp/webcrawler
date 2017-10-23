# -*- coding: utf-8 -*-
import logging
import re

from bs4 import BeautifulSoup
import eventlet
from eventlet.green import urllib2

from models.url_helpers import (
    ensure_http_scheme,
    url_path,
    top_level_domain,
    is_valid_url,
    link_from_domain_or_none,
    is_relevant_asset,
    get_link_from_asset,
    build_asset_url
)

logging.getLogger(__name__)


class Page:

    FETCH_TIMEOUT_SECONDS = 5
    MAX_RETRIES = 3

    def __init__(self, url):
        self.url = ensure_http_scheme(url)
        self.path = url_path(url)
        self.domain = top_level_domain(self.url)
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

    def extract_internal_links(self):
        # type: (Page) -> set
        if not self._internal_links:
            soup = BeautifulSoup(self.get_html(), 'html.parser')
            anchors = soup.find_all('a')
            internal_links = set()

            for anchor in anchors:
                href = anchor.get('href')
                internal_link = link_from_domain_or_none(href, self.domain)
                internal_link_with_protocol = ensure_http_scheme(internal_link)

                if internal_link_with_protocol:
                    internal_links.add(internal_link_with_protocol)

            self._internal_links = internal_links

        return self._internal_links

    def extract_assets(self):
        if not self._assets:
            soup = BeautifulSoup(self.get_html(), 'html.parser')
            assets = soup.find_all(is_relevant_asset)
            output_assets = set()

            for asset in assets:
                asset_link = get_link_from_asset(asset)
                cleaned = asset_link.replace('../', '')
                cleaned = re.sub('^//', '/', cleaned)

                if cleaned.startswith('?') or cleaned.startswith('#'):
                    continue

                formatted_output = build_asset_url(cleaned)
                output_assets.add(formatted_output)

            self._assets = output_assets

        return self._assets

    def print_assets(self):
        """Prints references inside tags: a, img, script, link"""
        print '\n', 'Assets for {} :'.format(self.url)
        for asset in sorted(list(self.extract_assets)):
            print '\t', asset
        print '\n'



