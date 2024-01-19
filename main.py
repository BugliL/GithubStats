import os
import logging
import requests
from datetime import datetime
from pprint import pprint

logging.basicConfig(level=logging.ERROR)

today_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

query = f"""
query {{
  viewer {{
    pullRequests(
        states: [OPEN, MERGED], 
        first: 20, orderBy: {{field: CREATED_AT, direction: DESC}}
    ) {{
      nodes {{
        title
        createdAt
        author {{
            login
        }}
      }}
    }}
    repositories(first: 10, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
      nodes {{
        name
        createdAt
      }}
    }}
  }}
}}
"""  # noqa: F541

# Esegui la query GraphQL
today_date = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
github_token = os.environ.get("GITHUB_TOKEN")
headers = {"Authorization": f"bearer {github_token}"}
url = "https://api.github.com/graphql"
response = requests.post(url, json={"query": query}, headers=headers)
data = response.json()

# Stampa i risultati
pprint(data, indent=2,compact=False, width=200)