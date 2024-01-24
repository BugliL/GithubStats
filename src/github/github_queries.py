import os

organization = os.environ.get("GITHUB_ORGANIZATION")
repository = os.environ.get("GITHUB_REPOSITORY")
token = os.environ.get("GITHUB_TOKEN")
user = os.environ.get("GITHUB_USER")

reviews_query = f"""
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