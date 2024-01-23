import os
import logging
from pprint import pprint
import re
from typing import Any
import requests
from datetime import datetime, timedelta
import pandas as pd

from queries import reviews_query

logging.basicConfig(level=logging.ERROR)


class GithubClient(object):
    def __init__(self) -> None:
        self.token = os.environ.get("GITHUB_TOKEN")

    def download_reviews_data(self):
        headers = {"Authorization": f"bearer {self.token}"}
        url = "https://api.github.com/graphql"
        response = requests.post(url, json={"query": reviews_query}, headers=headers)
        return response.json()


class GithubParser(object):
    def __init__(self, data: dict[str, Any]) -> None:
        self.reviews = data  # type: dict[str, Any]
        self.review_actions = []  # type: list[dict[str, Any]]
        self.review_dataframe = None  # type: pd.DataFrame | None

    def parse_reviews(self) -> pd.DataFrame:
        self.review_actions = [
            {
                "url": pr["node"]["url"],
                "number": pr["node"]["number"],
                "repository": repo["name"],
                "pull_request": pr["node"]["title"],
                "assignee": pr["node"]["author"]["login"],
                "state": pr["node"]["state"],
                "review_state": review[0],
                "review_date": review[1],
            }
            for repo in self.reviews["data"]["organization"]["repositories"]["nodes"]
            for pr in repo["pullRequests"]["edges"]
            for review in set(
                (r["state"], r["updatedAt"]) for r in pr["node"]["reviews"]["nodes"]
            )
        ]

        df = pd.DataFrame(parser.review_actions)

        # filtered by date and grouped by pull request
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        reviewed = df[df["review_date"] > yesterday]

        # group data by pull request and get the last review_state
        self.review_dataframe = reviewed.sort_values("review_date", ascending=False)
        return self.review_dataframe

    def to_text(self) -> str:
        if self.review_dataframe is None:
            return ""

        def get_comment(action):
            return {
                "APPROVED": "Approvato",
                "CHANGES_REQUESTED": "Richiesta una modifica",
                "COMMENTED": "Riguardato",
                "DISMISSED": "Rimossa l'apporvazione",
            }.get(action["review_state"], action["review_state"])

        def get_ticket(action):
            result = re.findall(r"([A-Z]{3,5}-\d+)", action["pull_request"])
            return "" if not result else result[0]

        def get_author(action):
            return action["assignee"]

        def action_to_string(action) -> str:
            action1 = action.to_dict()
            return f"{get_ticket(action1)} {get_comment(action1)} PR di @{get_author(action1)} {action1['url']}"

        return "\n".join(self.review_dataframe.groupby(by="number").first().reset_index() .apply(action_to_string, axis=1).to_list())


if __name__ == "__main__":
    client = GithubClient()
    parser = GithubParser(client.download_reviews_data())
    parser.parse_reviews()
    pprint(parser.to_text(), width=200, compact=False)
