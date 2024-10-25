from typing import Dict, Literal

from mindvault.bookmarks.browser.custom_types import BrowserName, OSName


USER_DATA_DIRS: Dict[BrowserName, Dict[OSName, str]] = {
    "Chrome": {
        "Windows": r"~\AppData\Local\Google\Chrome\User Data",
        "Mac": r"~/Library/Application Support/Google/Chrome",
        "Linux": r"~/.config/google-chrome",
    },
    "Microsoft Edge": {
        "Windows": r"~\AppData\Local\Microsoft\Edge\User Data",
        "Mac": r"~/Library/Application Support/Microsoft Edge",
        "Linux": r"~/.config/microsoft-edge",
    },
    "Brave": {
        "Windows": r"~\AppData\Local\BraveSoftware\Brave-Browser",
        "Mac": r"~/Library/Application Support/BraveSoftware/Brave-Browser",
        "Linux": r"~/.config/BraveSoftware/Brave-Browser",
    },
}
