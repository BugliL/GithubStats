import os
import logging
import re
import requests
from datetime import datetime, timedelta
import pandas as pd

from queries import reviews_query

logging.basicConfig(level=logging.ERROR)

today = datetime.utcnow().strftime("%Y-%m-%d")
yesterday = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%d")
token = os.environ.get("GITHUB_TOKEN")

if __name__ == "__main__":
    # Execute the query
    headers = {"Authorization": f"bearer {token}"}
    url = "https://api.github.com/graphql"
    response = requests.post(url, json={"query": reviews_query}, headers=headers)
    data = response.json()

    actions = [
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
        for repo in data["data"]["organization"]["repositories"]["nodes"]
        for pr in repo["pullRequests"]["edges"]
        for review in set(
            (r["state"], r["updatedAt"]) for r in pr["node"]["reviews"]["nodes"]
        )
    ]

    df = pd.DataFrame(actions)

    # filtered by date and grouped by pull request
    reviewed = df[df["review_date"] > yesterday]


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


    print(reviewed.head())
    # for action in df:
    #     if action["review_date"][:10] == today:
    #         comment = get_comment(action)
    #         ticket = get_ticket(action)
    #         author = action["assignee"]
    #         print(
    #             f"{ticket} {comment} PR di @{author} {action['repository']} {action['url']}"
    #         )

    # # Print result
    # pprint(rs, width=200, compact=False, sort_dicts=True, indent=2)
