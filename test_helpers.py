import url_helpers
from models.page import Page


def test_pages_set():
    pages = set()
    pages.add(Page('www.test.com'))
    pages.add(Page('www.test.com'))
    assert len(pages) == 1

def test_top_level_domain():
    cases = (
        'http://www.test.com',
        'http://www.test.com/?q=1',
        'http://www.test.com/hello?world',
        'http://www.test.com/jobs.html',
        'https://www.test.com',
        'https://www.test.com/hello/world?q=1',
        'www.test.com',
        'www.test.com#hello',
        'www.test.com/#',
        'www.test.com/?q=1',
        'www.test.com/drawer.js',
        'www.test.com/hello/world?q=1',
        'www.test.com/jobs.html',
    )
    for url in cases:
        assert url_helpers.top_level_domain(url) == 'test.com'

def test_url_path():
    cases = (
        ('http://www.test.com', ''),
        ('http://www.test.com/?q=1', '/'),
        ('http://www.test.com/hello?world', '/hello'),
        ('http://www.test.com/jobs.html', '/jobs.html'),
        ('https://www.test.com', ''),
        ('https://www.test.com/hello/world?q=1', '/hello/world'),
        ('www.test.com', ''),
        ('www.test.com#hello', ''),
        ('www.test.com.1', ''),
        ('www.test.com/#', '/'),
        ('www.test.com/?q=1', '/'),
        ('www.test.com/drawer.js', '/drawer.js'),
        ('www.test.com/hello/world?q=1', '/hello/world'),
        ('www.test.com/jobs.html', '/jobs.html'),
    )
    for case in cases:
        assert url_helpers.url_path(case[0]) == case[1]

def test_is_valid_url():
    cases = (
        'http://www.test.com',
        'http://www.test.com/?q=1',
        'http://www.test.com/hello?world',
        'http://www.test.com/jobs.html',
        'https://www.test.com',
        'https://www.test.com/hello/world?q=1',
        'www.test.com',
        'www.test.com/#',
        'www.test.com/?q=1',
        'www.test.com/drawer.js',
        'www.test.com/hello/world?q=1',
        'www.test.com/jobs.html',
    )
    for url in cases:
        assert url_helpers.is_valid_url(url) == True

def test_is_not_valid_url():
    cases = (
        'www.test.com#hello',
    )
    for url in cases:
        assert url_helpers.is_valid_url(url) == False


def test_ensure_http_scheme():
    cases = (
        ('http://www.test.com', 'http://www.test.com'),
        ('https://www.test.com/hello/world?q=1', 'https://www.test.com/hello/world?q=1'),
        ('www.test.com', 'http://www.test.com'),
        ('test.com', 'http://test.com'),
        ('test.io', 'http://test.io'),
    )
    for case in cases:
        assert url_helpers.ensure_http_scheme(case[0]) == case[1]

def test_link_from_domain_or_none():
    cases = (
        ('https://plus.google.com/share?url=http%3A%2F%2Fwww.headspace.com', 'headspace.com', None),
        ('mailto:john@test.com', 'test.com', None),
        ('tel:123451234', 'test.com', None),
        #
        ('www.test.com', 'subdomain.test.com', 'http://www.test.com'),
        ('test.com', 'subdomain.test.com', 'http://test.com'),
        ('http://www.test.com', 'subdomain.test.com', 'http://www.test.com'),
        ('https://www.test.com', 'subdomain.test.com', 'https://www.test.com'),
        #
        ('www.test.com', 'test.com', 'http://www.test.com'),
        ('test.com', 'test.com', 'http://test.com'),
        ('http://www.test.com', 'test.com', 'http://www.test.com'),
        ('https://www.test.com', 'test.com', 'https://www.test.com'),
        #
        ('www.test.com', 'www.test.com', 'http://www.test.com'),
        ('test.com', 'www.test.com', 'http://test.com'),
        ('http://www.test.com', 'www.test.com', 'http://www.test.com'),
        ('https://www.test.com', 'www.test.com', 'https://www.test.com'),
        #
        ('www.test.com', 'http://www.test.com', 'http://www.test.com'),
        ('test.com', 'http://www.test.com', 'http://test.com'),
        ('http://www.test.com', 'http://www.test.com', 'http://www.test.com'),
        ('https://www.test.com', 'http://www.test.com', 'https://www.test.com'),
    )
    for case in cases:
        assert url_helpers.link_from_domain_or_none(case[0], case[1]) == case[2]


def test_build_asset_url():
    cases = (
        ('/home.js', 'www.test.com', 'http://www.test.com/home.js'),
        ('/home.js', 'test.com', 'http://test.com/home.js'),
        ('/home.js', 'http://www.test.com', 'http://www.test.com/home.js'),
        ('/home.js', 'https://www.test.com', 'http://www.test.com/home.js'),
        ('index.html', 'www.test.com', 'http://www.test.com/index.html'),
        ('index.html', 'test.com', 'http://test.com/index.html'),
        ('index.html', 'http://www.test.com', 'http://www.test.com/index.html'),
        ('index.html', 'https://www.test.com', 'http://www.test.com/index.html'),
    )
    for case in cases:
        assert url_helpers.build_asset_url(case[0], case[1]) == case[2]
