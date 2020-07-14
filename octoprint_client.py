import urequests as requests
import json
from time import sleep

OCTOPRINT_JOB_PATH = '/api/job'
OCTOPRINT_API_PATH = '/api/version'


class OctoPrintClient:

    def __init__(self, octoprint_url: str, api_key: str):
        self.octoprint_url = octoprint_url
        self.api_key = api_key

    def get_version_info(self):
        return self._get_request(url_path=OCTOPRINT_API_PATH)

    def get_job_info(self):
        headers = {'X-Api-Key': self.api_key}
        try:
            url = self.octoprint_url + OCTOPRINT_JOB_PATH
            response = requests.get(url, headers=headers)
            return json.loads(response.content.decode('utf-8'))
        except Exception as e:
            print(e)

    def _get_request(self, url_path: str = ""):
        url = self.octoprint_url + url_path
        headers = {'X-Api-Key': self.api_key}
        response = requests.get(url, headers=headers)
        return json.loads(response.content.decode('utf-8'))
