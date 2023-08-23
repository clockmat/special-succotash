import logging

import feedparser

from . import config
from .dood import DoodStream
from .modules.entry_manager import LastEntriesManager
from .scraper import scrape_feed
from .ytdl import YTDL

log = logging.getLogger(__name__)


def istrue(value):
    return value and value.lower() in ("true", "1", "yes")


class Handler:
    def __init__(self):
        self.entries_manager = LastEntriesManager(config.DB_PATH)

        self.dood = DoodStream(config.required.DOODSTREAM_API_KEY)
        self.dood.clean_slots()

        self.ytdl = YTDL()

    def handle(self, entry, tag):
        log.info(f"{tag} Handling entry: {entry.name}")
        url = entry.url
        try:
            if entry.youtube_dl:
                url = self.ytdl.get_download_url(entry.url)
            self.dood.remote_upload(url, entry.name)
            log.info(f"{tag} Added to DoodStream")
            return True
        except Exception as err:
            log.info(f"{tag} Failed to add entry to dood: {err}")
            return False

    def get_rss_feed(self, no: int):
        feed = feedparser.parse(config[f"CONTENTS_{no}"])
        entries = []
        CONTENTS_YT = config[f"CONTENTS_{no}_YT"]
        CONTENTS_HTTP = config[f"CONTENTS_{no}_HTTP"]
        for entry in feed.entries:
            entry = {
                "name": entry.title,
                "url": entry.link,
            }
            if istrue(CONTENTS_YT):
                entry["youtube_dl"] = True
            if CONTENTS_HTTP:
                entry["url"] = CONTENTS_HTTP.format(name=entry["name"])
            entries.append(entry)
        return entries

    def get_feed(self, no: int):
        if config[f"CONTENTS_{no}_RSS"]:
            return self.get_rss_feed(no)
        else:
            return scrape_feed(no)

    def feed(self):
        entries = []
        for i in range(config.required.CONTENTS_COUNT):
            entries += self.get_feed(i + 1)
        return entries
