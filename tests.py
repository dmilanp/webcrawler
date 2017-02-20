import unittest

from models.page import Page


class TestPageClass(unittest.TestCase):

    html = """
        <html>
            <body>
                <a href="www.yoyowallet.com/jobs.html">"
                <a href="www.twitter.com/yoyowallet">"
                <img src="www.facebook.com/logo.jpg">"
            </body>"
            <script src="www.yoyowallet.com/drawer.js">"
        </html>
        """

    def test_set(self):
        pages = set()
        pages.add(Page("www.yoyowallet.com"))
        pages.add(Page("www.yoyowallet.com"))
        self.assertEqual(len(pages), 1)
        self.assertEqual(Page("www.yoyowallet.com"), Page("www.yoyowallet.com"))

    def test_valid_urls(self):
        self.assertTrue(Page("www.yoyowallet.com").has_valid_url())
        self.assertTrue(Page("http://www.yoyowallet.com").has_valid_url())
        self.assertTrue(Page("https://www.yoyowallet.com").has_valid_url())
        self.assertFalse(Page("ftp://www.yoyowallet.com.1").has_valid_url())
        self.assertFalse(Page("www.yoyowallet.com.1").has_valid_url())
        self.assertFalse(Page("hello.bye").has_valid_url())

    def test_ensure_protocol(self):
        self.assertEqual(Page.ensure_url_protocol("www.yoyowallet.com"), "http://www.yoyowallet.com")

    def test_extract_resource_from_url(self):
        self.assertEqual(Page.extract_path_from_url("www.yoyowallet.com/?q=1"), "/")
        self.assertEqual(Page.extract_path_from_url("www.yoyowallet.com/hello?world"), "/hello")
        self.assertEqual(Page.extract_path_from_url("www.yoyowallet.com/hello/world?q=1"), "/hello/world")

    def test_internal_links(self):
        p = Page("www.yoyowallet.com")
        p._html = self.html
        self.assertEqual(p.internal_links, ["www.yoyowallet.com/jobs.html"])

    def test_assets(self):
        p = Page("www.yoyowallet.com")
        p._html = self.html
        self.assertEqual(p.assets, ["www.yoyowallet.com/jobs.html", "www.twitter.com/yoyowallet",
                                    "www.facebook.com/logo.jpg", "www.yoyowallet.com/drawer.js"])


if __name__ == '__main__':
    unittest.main()
