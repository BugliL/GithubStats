import logging

from github_client import GithubClient
from github_parser import GithubParser

logging.basicConfig(level=logging.ERROR)

if __name__ == "__main__":
    client = GithubClient()
    parser = GithubParser()
    parser.add_review_data(client.download_reviews_data())
    parser.parse_reviews()
    print(parser.to_text())
