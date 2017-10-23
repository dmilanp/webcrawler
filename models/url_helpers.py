import re
from urlparse import urlparse

import tldextract
import validators


def top_level_domain(url):
    # type: (str) -> str
    _url = ensure_http_scheme(url)
    tld = tldextract.extract(_url)
    return "{}.{}".format(tld.domain, tld.suffix)


def url_path(url):
    _url = ensure_http_scheme(url)
    return urlparse(_url).path


def is_valid_url(url):
    # type: (str) -> bool
    """Checks if url is valid. Requires scheme in url."""
    _url = ensure_http_scheme(url)
    if validators.url(_url):
        return True
    return False


def ensure_http_scheme(url):
    # type: (str) -> str
    if not url:
        return None
    elif url.startswith('http'):
        return url
    else:
        return "http://" + url


def link_from_domain_or_none(link, domain):
    """If link is to same domain this returns it well formatted, otherwise returns None"""
    if link is None or 'mailto:' in link or 'tel:' in link:
        return None

    tld = top_level_domain(domain)

    if tld not in urlparse(ensure_http_scheme(link)).netloc:
        # Guard cases like https://plus.google.com/share?url=http%3A%2F%2Fwww.headspace.com
        return None
    else:
        _link = re.sub('[\./]+', '', link)
        return ensure_http_scheme(
            urlparse(domain).netloc + '/' + _link
        )


def is_relevant_asset(tag):
    return tag.name in ['a', 'link', 'img', 'script']


def get_link_from_asset(tag):
    if tag.name == 'a' or tag.name == 'link':
        return tag.get('href')
    elif tag.name == 'img' or tag.name == 'script':
        return tag.get('src')


def build_asset_url(asset, url):
    _url = ensure_http_scheme(url)
    parsed_url = urlparse(_url)

    if asset.startswith('/'):
        asset = re.sub('^/', '', asset)
        return '{}/{}'.format(parsed_url.netloc, asset)

    return ensure_http_scheme(asset)
