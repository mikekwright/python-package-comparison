import requests


class AppClient:
    def __init__(self, endpoint: str = 'http://localhost:5000'):
        self._endpoint = endpoint

    def get_index(self):
        return requests.get(self._endpoint).text
