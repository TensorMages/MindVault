"""Extracting and storing bookmarks from chromium browsers (currently Chrome, Brave and Edge supported)"""

__all__ = ['log_dir', 'bookmarks', 'BookmarkModel', 'ChromiumBrowser', 'ChromeBrowser', 'EdgeBrowser', 'BraveBrowser',
           'get_bookmarks_from_browser']

from typing import Literal

from models.browser import ChromiumBrowser
from models.browser import ChromeBrowser
from models.browser import EdgeBrowser
from models.browser import BraveBrowser
from models.bookmark import BookmarkModel

def get_bookmarks_from_browser(driver, userEmail,
    browser_name: Literal["chrome", "edge", "brave"], # type of browser to extract bookmarks from currently supported: chrome, edge, brave
) -> list[BookmarkModel]:
    """
    Extracts bookmarks from a specified browser.
    """
    browser_name = browser_name.lower()
    if browser_name == "chrome":
        browser = ChromeBrowser()
    elif browser_name == "edge":
        browser = EdgeBrowser()
    elif browser_name == "brave":
        browser = BraveBrowser()
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")
    return browser.extract_bookmarks(driver)
