import os
import logging
import requests

from github_queries import reviews_query

logging.basicConfig(level=logging.ERROR)


class GithubClient(object):
    url = "https://api.github.com/graphql"

    def __init__(self) -> None:
        self.token = os.environ.get("GITHUB_TOKEN")
        self.headers = {"Authorization": f"bearer {self.token}"}

    def download_reviews_data(self):
        return requests.post(
            self.url, json={"query": reviews_query}, headers=self.headers
        ).json()

 