import os

# Constants
GITHUB_BASE_URL = os.environ.get("GITHUB_BASE_URL", 'https://api.github.com')
VERTEX_PROJECT_ID = os.environ.get("VERTEX_PROJECT_ID")
VERTEX_LOCATION = os.environ.get("VERTEX_LOCATION", "us-central1")
GITHUB_SECRET_PROJECT_ID = os.environ.get("GITHUB_SECRET_GCPPROJECTID")
GITHUB_SECRET_NAME = os.environ.get("GITHUB_SECRET_GCPSECRETNAME")
