import os
import json
from loguru import logger
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel, Field

from models.bookmark import BookmarkModel

class ChromiumBrowser(BaseModel):
    """
    Base class for interacting with web browsers' bookmarks
    """

    name: str = Field(..., description="The name of the browser")
    user_data_dirs: Dict[str, str] = Field(
        ..., description="Paths to user data for different OS"
    )
    default_bookmarks_filename: str = Field(
        ..., description="Default filename for the bookmarks file"
    )
    operating_system: Optional[str] = Field(
        None, description="The current operating system"
    )
    user_data_dir_path: Optional[Path] = Field(
        None, description="Path to the user data directory"
    )

    def __init__(self, **data):
        super().__init__(**data)
        self._set_operating_system()
        self._set_user_data_dir_path()
        logger.info(f"Initialized {self.name} browser on {self.operating_system}")
        logger.info(f"User bookmark directory path: {self.user_data_dir_path}")

    def _set_operating_system(self):
        self.operating_system = "Mac"
        # if "win" in sys.platform.lower():
        #     self.operating_system = "Windows"
        # elif "mac" in sys.platform.lower():
        #     self.operating_system = "Mac"
        # elif "linux" in sys.platform.lower():
        #     self.operating_system = "Linux"
        # else:
        #     self.operating_system = "Unknown"
        #     logger.warning(f"Unsupported operating system: {self.operating_system}")

    def _set_user_data_dir_path(self):
        if self.operating_system in self.user_data_dirs:
            self.user_data_dir_path = Path(
                os.path.expanduser(self.user_data_dirs[self.operating_system])
            )
        else:
            raise ValueError(f"Unsupported operating system: {self.operating_system}")

    def get_bookmark_files(self):
        chrome_path = Path(self.user_data_dir_path)
        # find all bookmarks files
        bookmarks_files = list(chrome_path.glob("**/*Bookmarks"))
        logger.info(f"Found {len(bookmarks_files)} bookmarks files")
        # Ignore the snapshot files
        bookmarks_files = [
            file.as_posix()
            for file in bookmarks_files
            if "Snapshot" not in file.as_posix()
        ]
        return bookmarks_files

    def extract_bookmark_info(
        self,
        driver,
        bookmarks_file_path: str,  # path to the bookmarks file
    ) -> list[BookmarkModel]:
        """Extracts bookmark information from a Chrome Bookmarks file."""
        with open(bookmarks_file_path, "r", encoding="utf-8") as f:
            bookmarks_data = json.load(f)

        bookmarks = []

        def traverse_bookmarks(node, folder=None):
            """Recursively traverses the bookmark tree."""
            if node["type"] == "url":
                date_added = self._convert_timestamp(node["date_added"])
                bookmark = BookmarkModel(
                    name=node["name"],
                    url=node["url"],
                    folder=folder,
                    dateAdded=date_added,
                )
                bookmarks.append(bookmark)
                bookmark.create_node(driver)
            elif node["type"] == "folder":
                for child in node["children"]:
                    traverse_bookmarks(child, folder=node["name"])

        for root_name, root_node in bookmarks_data["roots"].items():
            traverse_bookmarks(root_node, folder=root_name)

        return bookmarks

    def extract_bookmarks(self, driver) -> list[BookmarkModel]:
        """Extracts all Chrome Bookmarks from all profiles."""
        bookmarks_files = self.get_bookmark_files()
        bookmarks = []
        for bookmarks_file in bookmarks_files:
            bookmarks.extend(self.extract_bookmark_info(driver, bookmarks_file))
        if len(bookmarks) == 0:
            logger.error(f"No bookmarks found in {self.name}")
            raise ValueError(f"No bookmarks found in {self.name}")
        else:
            logger.info(f"Extracted {len(bookmarks)} bookmarks")
        return bookmarks

    def _convert_timestamp(self, timestamp: int) -> datetime:
        # Convert WebKit timestamp (microseconds since 1601-01-01) to datetime
        windows_epoch = datetime(1601, 1, 1)
        delta = timedelta(microseconds=int(timestamp))
        return (windows_epoch + delta).date()

class ChromeBrowser(ChromiumBrowser):
    name: str = "Chrome"
    user_data_dirs: Dict[str, str] = {
        "Windows": r"~\AppData\Local\Google\Chrome\User Data", # TODO: Use linux style path if possible
        "Mac": r"~/Library/Application Support/Google/Chrome",
        "Linux": r"~/.config/google-chrome",
    }
    default_bookmarks_filename: str = "Bookmarks"

class EdgeBrowser(ChromiumBrowser):
    name: str = "Microsoft Edge"
    user_data_dirs: Dict[str, str] = {
        "Windows": r"~\AppData\Local\Microsoft\Edge\User Data",
        "Mac": r"~/Library/Application Support/Microsoft Edge",
        "Linux": r"~/.config/microsoft-edge",
    }
    default_bookmarks_filename: str = "Bookmarks"

class BraveBrowser(ChromiumBrowser):
    name: str = "Brave"
    user_data_dirs: Dict[str, str] = {
        "Windows": r"~\AppData\Local\BraveSoftware\Brave-Browser",
        "Mac": r"~/Library/Application Support/BraveSoftware/Brave-Browser",
        "Linux": r"~/.config/BraveSoftware/Brave-Browser",
    }
    default_bookmarks_filename: str = "Bookmarks"