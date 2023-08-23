import json
import logging
from time import sleep

import requests
from bs4 import BeautifulSoup

from . import config

log = logging.getLogger(__name__)


def parse_feed(content: str, base_url: str = ""):
    entries = []
    soup = BeautifulSoup(content, "html.parser")
    for post in soup.select(
        "#content_div > div.main_content > div.blog_posts > div > div.post_el_wrap"
    ):
        name = post.select_one("div.post_text").text
        url = base_url + post.select_one("div.post_el_wrap > a").attrs["href"]
        entries.append(
            {
                "name": name,
                "url": url,
            }
        )
    return entries


def fetch_feed(url, base_url, cookies, retry: int = 10):
    for _ in range(retry):
        try:
            r = requests.get(url=url, cookies=cookies)
            if r.status_code == 200:
                return parse_feed(content=r.text, base_url=base_url)
        except Exception as err:
            log.debug(f"[{_+1}/{retry}] Failed to fetch content: {err}")
            sleep(1)
    return []


def scrape_feed(no: int):
    entries = []
    content_urls = [
        link.strip() for link in config.required[f"CONTENTS_{no}"].split("\n")
    ]
    cookies = json.loads(config.required[f"CONTENTS_{no}_COOKIES"])
    for url in content_urls:
        base_url = "/".join(url.split("/")[:3])
        entries += fetch_feed(url, base_url=base_url, cookies=cookies)

    entries = list({x["url"]: x for x in entries}.values())
    return entries
