import os
import pandas as pd
from typing import Any
from datetime import datetime, timedelta
from github_formatter import format_result

USER = os.environ.get("GITHUB_USER")


class GithubParser(object):
    def __init__(self) -> None:
        self.reviews = None  # type: dict[str, Any] | None
        self.review_actions = []  # type: list[dict[str, Any]]
        self.review_dataframe = None  # type: pd.DataFrame | None

    def add_review_data(self, data: dict[str, Any]) -> None:
        self.reviews = data

    def parse_reviews(self) -> pd.DataFrame:
        if self.reviews is None:
            self.review_dataframe = pd.DataFrame()
            return self.review_dataframe

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
                (r["state"], r["updatedAt"])
                for r in (
                    pr["node"]["reviews"]["nodes"]
                    or [{"state": None, "updatedAt": None}]
                )
            )
        ]

        df = pd.DataFrame(self.review_actions)

        # filtered by date and grouped by pull request
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
        reviewed = df[(df["review_date"] > yesterday) | (df["review_date"].isnull())]
        reviewed = df[(df["assignee"] == USER) | (df["review_state"].notnull())]

        # group data by pull request and get the last review_state
        self.review_dataframe = reviewed.sort_values("review_date", ascending=False)
        return self.review_dataframe

    def to_text(self) -> str:
        return format_result(self.review_dataframe)
