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
    if not (url.startswith('https://') or url.startswith('http://')):
        return "http://" + url
    return url


def extract_path_from_url(url):
    """Returns resource part of url without domain"""
    return urlparse(ensure_url_protocol(url)).path