import re
from urlparse import urlparse

import tldextract
import validators


def domain_for_url(url):
    tld = tldextract.extract(url)
    return "{}.{}".format(tld.domain, tld.suffix)


def is_valid_url(url):
    """Checks if url is valid"""
    if not validators.url(ensure_url_protocol(url)):
        return False
    return True


def ensure_url_protocol(url):
    """If protocol not provided fallback to http"""
    if not url:
        return None

    if not (url.startswith('https://') or url.startswith('http://')):
        return "http://" + url

    return url


def extract_path_from_url(url):
    """Returns resource part of url without domain"""
    return urlparse(ensure_url_protocol(url)).path


def link_from_domain_or_none(link, domain):
    """If link is to same domain this returns it well formatted, otherwise returns None"""
    if (not link or
            'mailto:' in link or
            'tel:' in link):
        return None

    if domain not in urlparse(link).netloc:
        # Guard cases like https://plus.google.com/share?url=http%3A%2F%2Fwww.headspace.com
        return None

    if domain in link:
        link = ensure_url_protocol(link)
        link_with_clean_slashes = re.sub('http://[/]+', 'http://', link)
        return link_with_clean_slashes
    else:
        # Relative link
        link = link.replace('../', '')
        link = re.sub('^/', '', link)
        return ensure_url_protocol(
            urlparse(domain).netloc + '/' + link
        )


def is_asset(tag):
    return tag.name in ['a', 'link', 'img', 'script']


def get_asset_link(tag):
    if tag.name == 'a' or tag.name == 'link':
        return tag.get('href')
    elif tag.name == 'img' or tag.name == 'script':
        return tag.get('src')


def prepare_asset(asset, url):
    parsed_url = urlparse(url)
    if asset.startswith('www'):
        return ensure_url_protocol(asset)
    elif asset.startswith('http'):
        return asset
    elif asset.startswith('/'):
        asset = re.sub('^/', '', asset)
        return '{}/{}'.format(parsed_url.netloc, asset)