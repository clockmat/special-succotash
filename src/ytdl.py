import random

from youtube_dl import YoutubeDL


class YTDL:
    def __init__(self, debug: bool = False, proxies: list = None):
        self.proxies = proxies
        self.debug = debug

    @property
    def random_proxy(self):
        if self.proxies and len(self.proxies) > 0:
            return random.choice(self.proxies)

    def get_video_info(self, link: str) -> dict:
        ydl_opts = {}

        if self.proxies:
            ydl_opts["proxy"] = self.random_proxy
        if not self.debug:
            ydl_opts["quiet"] = True

        yt = YoutubeDL(ydl_opts)
        info = yt.extract_info(link, download=False)
        return info

    def get_download_url(self, link: str) -> str:
        return self.get_video_info(link)["url"]
