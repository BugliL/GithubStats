import json
import os
import logging
import requests
from datetime import datetime

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
      first: 10 
      orderBy: {{field: UPDATED_AT, direction: DESC}}
    ) {{
      nodes {{
        name
        pullRequests(
          first: 20
          states: [OPEN, MERGED]
          orderBy: {{field: CREATED_AT, direction: DESC}}
        ) {{
          edges {{
            node {{
              ... on PullRequest {{
                title
                createdAt
                updatedAt
                state
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

# Print results
print(json.dumps(data, indent=2, sort_keys=True))
