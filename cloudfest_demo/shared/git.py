from typing import Annotated, TYPE_CHECKING
import requests

from github import Auth, Github
from github.GithubException import GithubException  # Import GithubException
from pydantic import BaseModel

if TYPE_CHECKING:
    from .review import ReviewComment


class GitClientError(Exception):
    """Base class for exceptions in the Git client."""


class InvalidRepoNameError(GitClientError):
    """Raised when an invalid repository name is provided."""


class DiffRetrievalError(GitClientError):
    """Raised when there's an issue retrieving the diff from GitHub."""


class FileDownloadError(GitClientError):
    """Raised when there's an issue downloading a file from GitHub."""

class CommentPostError(GitClientError):
    """Raised when an issue occurred while posting a comment"""


class PrDetails(BaseModel):
    owner: Annotated[str, "Owner of the repository"]
    repo: Annotated[str, "Repository name"]
    pull_number: Annotated[int, "Pull Request number"]
    title: Annotated[str, "Title of the PR"]
    description: Annotated[str, "Description of the PR"] | None



def get_client(app_id: int, installation_id: int, private_key: str, base_url: str) -> Github:
    """
    Retrieve an authenticated GitHub client instance using App authentication.

    This function accesses secret information to authenticate as a GitHub App and
    returns a client instance that can be used to interact with the GitHub API.

    Returns:
        Github: An authenticated GitHub client object.
    """
    auth = Auth.AppAuth(
        app_id=app_id,
        private_key=private_key,
    ).get_installation_auth(installation_id=installation_id)

    with Github(base_url=base_url, auth=auth) as github:
        return github


def get_pr_details(github_client, repo_full_name, pull_number) -> PrDetails:
    """Retrieves details of the pull request from GitHub API."""

    owner, repo = repo_full_name.split("/")

    repo = github_client.get_repo(repo_full_name)
    pr = repo.get_pull(pull_number)

    return PrDetails(owner=owner, repo=repo.name, pull_number=pull_number, title=pr.title, description=pr.body)


def get_pr_diff(github_client: Github, repo_name: str, pull_number: int) -> str:
    """
    Fetches the diff of a specific pull request from the GitHub API.

    Args:
        github_client: An authenticated GitHub client instance.
        owner: The owner of the repository.
        repo: The name of the repository.
        pull_number: The pull request number.

    Returns:
        The diff of the pull request as a string, or an empty string if an error occurred.

    Raises:
        requests.exceptions.RequestException: If an error occurs during the HTTP request.
        ValueError: If the repository name is invalid.
    """

    if not repo_name or "/" not in repo_name:
        raise InvalidRepoNameError(f"Invalid repository name: {repo_name}")

    print(f"Attempting to get diff for: {repo_name} PR#{pull_number}")

    api_url = f"https://api.github.com/repos/{repo_name}/pulls/{pull_number}"
    headers = {
        'Authorization': f'Bearer {github_client.requester.auth.token}',  # Use Bearer token for authentication.
        'Accept': 'application/vnd.github.v3.diff'  # Specify the diff format.
    }

    try:
        response = requests.get(f"{api_url}.diff", headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for bad status codes.

        diff = response.text
        print(f"Retrieved diff length: {len(diff)}")
        return diff
    except requests.exceptions.RequestException as e:
        raise DiffRetrievalError(f"Failed to get diff. HTTP error: {e}") from e
    except Exception as e:
        raise DiffRetrievalError(f"An unexpected error occurred while getting the diff: {e}") from e


def download_file_snapschot_from_pr(github_client, repo_name, pr_number, file_path):
    if not repo_name or "/" not in repo_name:
        raise InvalidRepoNameError(f"Invalid repository name: {repo_name}")
    # Get the repository
    try:
        repo = github_client.get_repo(f"{repo_name}")

        # Get the pull request
        pr = repo.get_pull(pr_number)
    except GithubException as e:
        raise FileDownloadError(f"Failed to interact with Github api to get repo and PR: {e}") from e

    # Get the head branch name
    base_branch = pr.base.ref

    # Construct the URL to the file in the head branch
    file_url = f"https://raw.githubusercontent.com/{repo_name}/{base_branch}/{file_path}"

    # Include the token in the headers for authentication
    headers = {'Authorization': f'token {github_client.requester.auth.token}'}

    # Download the file
    try:
        file_response = requests.get(file_url, headers=headers, timeout=10)
        # Check for 404 specifically (file not found)
        if file_response.status_code == 404:
            return f"File not found in base branch: {file_path}"
        file_response.raise_for_status()

        return file_response.text
    except requests.exceptions.RequestException as e:
        raise FileDownloadError(f"Failed to download file: {file_response.status_code}. HTTP Error: {e}") from e
    except Exception as e:
        raise FileDownloadError(f"Failed to download file due to an unexpected error: {e}") from e



def post_comment(github_client, repo_full_name, pull_number, comment):
    """Retrieves details of the pull request from GitHub API."""
    try:
        repo = github_client.get_repo(repo_full_name)
        pr = repo.get_pull(pull_number)
        return pr.create_issue_comment(comment)
    except GithubException as e:
        raise CommentPostError(f"Failed to post comment to the PR. Github Error: {e}") from e
    except Exception as e:
        raise CommentPostError(f"Failed to post comment to the PR. Unexpected error: {e}") from e


def comment_to_dict(comment: 'ReviewComment') -> dict:

    output = {
        "path": comment.path,
        "body": comment.body,
        "line": comment.line,
        "side": comment.side,
        "start_side": comment.start_side,
        }
    if comment.start_line !=comment.line:
        output.update({"start_line": comment.start_line})
    return output

def post_pr_review(
    github_client,
    repo_full_name,
    pull_number,
    summary,
    comments: list['ReviewComment'],
):
    """Submits the review comments to the GitHub API."""
    print(f"Attempting to create review with {len(comments)} review comments")
    review_comments = [
            comment_to_dict(comment)
            for comment in comments
        ]

    try:
        repo = github_client.get_repo(repo_full_name)
        pr = repo.get_pull(pull_number)
        return pr.create_review(
            body=summary,
            comments=review_comments,
            event="COMMENT"
        )

    except Exception as e:
        print(f"Error creating review: {str(e)}")
        print(f"Error type: {type(e)}")
        print(f"Review payload: {comments}")
