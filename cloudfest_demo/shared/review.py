from typing import Annotated,List, Literal

import json
from pydantic import BaseModel, field_validator

from .diff import FileDiff, UnifiedDiff
from .git import PrDetails


class ReviewComment(BaseModel):

    @field_validator("start_side", "side", mode='before')
    def upper_side(cls, value):
        return value.upper()

    path: Annotated[str, "Path to the file"]
    start_line: Annotated[int, "Start line of the comment"] | None
    line: Annotated[int, "End line of the comment"]
    body: Annotated[str, "Comment body"]
    start_side: Annotated[Literal['LEFT', 'RIGHT'], "Start Side of the diff"]
    side: Annotated[Literal['LEFT', 'RIGHT'], "End Side of the diff"]

class ReviewFile(BaseModel):
    path: Annotated[str | None, "Path to the file"] = None
    diff: Annotated[FileDiff | None, "Git Diff content"] = None
    pr_details: Annotated[PrDetails, "PR Details"]
    snapshot: Annotated[str | None, "Head file content"] = None


def convert_diff_to_review_files(unified_diff: "UnifiedDiff", pr_details: PrDetails) -> List[ReviewFile]:
    review_files: List[ReviewFile] = []
    for file_diff in unified_diff.files:
        review_file = ReviewFile(
            path=file_diff.new_file,  # or file_diff.old_file if preferred
            diff=file_diff,
            pr_details=pr_details,
        )
        review_files.append(review_file)
    return review_files

def is_valid_json(response_text: str) -> bool:
    """Check if the response text is valid JSON."""
    try:
        json.loads(response_text)
        return True
    except json.JSONDecodeError:
        return False

def parse_review_comments(response_text: str) -> list[ReviewComment]:
    """Parse the JSON response text into a list of ReviewComment objects."""

    if response_text.startswith('```json'):
        response_text = response_text[7:]
    if response_text.endswith('```'):
        response_text = response_text[:-3]
    response_text = response_text.strip()

    if not is_valid_json(response_text):
        print("Error: Response is not valid JSON.")
        print(f"Raw response: {response_text}")
        return []

    data = json.loads(response_text)
    if "reviews" not in data or not isinstance(data["reviews"], list):
        print("Error: Response doesn't contain a valid 'reviews' array.")
        print(f"Response content: {data}")
        return []

    reviews = []
    for review_item in data["reviews"]:
        # Validate required fields
        required_fields = ["path", "start_line", "line", "body", "start_side", "side"]
        if all(field in review_item for field in required_fields):
            try:
                review = ReviewComment(**review_item)
                reviews.append(review)
            except Exception as e:
                print(f"Error validating review item {review_item}: {e}")
        else:
            print(f"Invalid review format (missing required fields): {review_item}")
            return []

    return reviews