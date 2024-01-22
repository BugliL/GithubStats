import os
import logging
import re
import requests
from datetime import datetime
from pprint import pprint

logging.basicConfig(level=logging.ERROR)

today = datetime.utcnow().strftime("%Y-%m-%dT00:00:00Z")
organization = os.environ.get("GITHUB_ORGANIZATION")
repository = os.environ.get("GITHUB_REPOSITORY")
token = os.environ.get("GITHUB_TOKEN")
user = os.environ.get("GITHUB_USER")

query = f"""
query PRReviewers {{
  organization(login: "{organization}") {{
    repositories(
      first: 100
      orderBy: {{field: UPDATED_AT, direction: DESC}}
    ) {{
      nodes {{
        name
        pullRequests(
          first: 100
          states: [OPEN, MERGED]
          orderBy: {{field: CREATED_AT, direction: DESC}}
        ) {{
          edges {{
            node {{
              ... on PullRequest {{
                title
                createdAt
                updatedAt
                number
                state
                url
                reviews(first: 20, author: "{user}") {{
                  totalCount
                  nodes {{
                    state
                    updatedAt
                  }}
                }}
                author {{
                  login
                }}
              }}
            }}
          }}
        }}
      }}
    }}
  }}
}}
"""

# Execute the query
headers = {"Authorization": f"bearer {token}"}
url = "https://api.github.com/graphql"
response = requests.post(url, json={"query": query}, headers=headers)
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
        (r["state"], r["updatedAt"][:10]) for r in pr["node"]["reviews"]["nodes"]
    )
]

# TODO: filter by date so we can run it every day and get the actions of the day
# TODO: group by pull request and get the last action

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


for action in actions:
    comment = get_comment(action)
    ticket = get_ticket(action)
    print(f"{comment} su {action['repository']} {ticket} #{action['number']}")

# Print result
# pprint(rs, width=200, compact=False, sort_dicts=True, indent=2)
