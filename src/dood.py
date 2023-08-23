import logging
import sys
from datetime import datetime, timedelta

import requests

logging.getLogger("urllib3").setLevel(logging.WARNING)
log = logging.getLogger(__name__)


class DoodStream:
    def __init__(self, api_key, base_url="https://doodapi.com/api"):
        self.base_url = base_url
        self.api_key = api_key

    def req(self, cmd: str, params: dict = {}):
        params["key"] = self.api_key
        url = f"{self.base_url}/{cmd}"
        try:
            r = requests.get(url=url, params=params)
            response = r.json()
            if response["msg"] in ("Wrong Auth", "Invalid key"):
                log.error("Invalid DoodStream API key")
                sys.exit(1)

            elif response["status"] > 399:
                log.error(response["msg"])
                sys.exit(1)
            else:
                return response
        except ConnectionError as e:
            log.error(f"Connection error: {e}")
            sys.exit(1)

    def account_info(self):
        return self.req("account/info")

    def account_reports(self):
        return self.req("account/stats")

    def remote_upload(self, direct_link, new_name=None, folder_id=None):
        if self.remaining_slots() == 0:
            raise Exception("No remote upload slots available")

        params = {"url": direct_link}
        if new_name:
            params["new_name"] = new_name
        if folder_id:
            params["fld_id"] = folder_id
        return self.req(cmd="upload/url", params=params)

    def file_info(self, file_id):
        return self.req("file/info", params={"file_code": file_id})

    def search_videos(self, search_keyword):
        return self.req("file/search", params={"q": search_keyword})

    def rename_file(self, file_id, name):
        return self.req("file/rename", params={"file_code": file_id, "name": name})

    def copy_video(self, file_id):
        return self.req("file/copy", params={"file_code": file_id})

    def remote_upload_slots(self):
        res = self.req("urlupload/slots")
        res["remaining_slots"] = int(res["total_slots"]) - int(res["used_slots"])
        return res

    def remaining_slots(self):
        self.remote_upload_slots()["remaining_slots"]

    def remote_upload_action(
        self,
        restart_errors=None,
        clear_errors=None,
        clear_all=None,
        delete_code=None,
    ):
        params = {}
        if restart_errors:
            params["restart_errors"] = True
        if clear_errors:
            params["clear_errors"] = True
        if clear_all:
            params["clear_all"] = True
        if delete_code:
            params["delete_code"] = delete_code
        return self.req("urlupload/actions", params=params)

    def delete_invalid_url_upload(self):
        res = self.req("urlupload/list")
        for file in res["result"]:
            if file["bytes_total"] > 5000000000 or (
                file["status"] == "error"
                and datetime.now() - datetime.fromisoformat(file["created"])
                > timedelta(hours=3)
            ):
                self.remote_upload_action(delete_code=file["file_code"])

    def clean_slots(self):
        self.delete_invalid_url_upload()
        self.remote_upload_action(restart_errors=True)
