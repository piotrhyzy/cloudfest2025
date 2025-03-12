import re
from typing import Literal, Union

from pydantic import BaseModel

# diff

class UnchangedLine(BaseModel):
    type: Literal['unchanged'] = 'unchanged'
    line: str
    old_line_number: int
    new_line_number: int
    side: Literal['both'] = 'both'


class RemovedLine(BaseModel):
    type: Literal['removed'] = 'removed'
    line: str
    line_number: int
    side: Literal['left'] = 'left'


class AddedLine(BaseModel):
    type: Literal['added'] = 'added'
    line: str
    line_number: int
    side: Literal['right'] = 'right'


Lines = Union[UnchangedLine, RemovedLine, AddedLine]


class Hunk(BaseModel):
    old_start: int
    old_length: int
    new_start: int
    new_length: int
    changes: list[Lines]


class FileDiff(BaseModel):
    old_file: str
    new_file: str
    hunks: list[Hunk]


class UnifiedDiff(BaseModel):
    files: list[FileDiff]



file_header_old_re = re.compile(r'^--- a/(.*)$')
file_header_new_re = re.compile(r'^\+\+\+ b/(.*)$')
hunk_header_re = re.compile(r'^@@ -(\d+),?(\d*) \+(\d+),?(\d*) @@')


def parse_file_headers(lines: list[str], start_index: int) -> tuple[str, str, int] | None:
    """Parse file headers starting from start_index in lines.
    Returns a tuple of (old_file, new_file, next_index) or None if no valid file header is found."""
    if start_index >= len(lines):
        return None

    old_file_match = file_header_old_re.match(lines[start_index])
    if not old_file_match:
        return None

    old_file = old_file_match.group(1)
    next_index = start_index + 1
    if next_index >= len(lines):
        return None

    new_file_match = file_header_new_re.match(lines[next_index])
    if not new_file_match:
        return None

    new_file = new_file_match.group(1)
    return (old_file, new_file, next_index + 1)


def parse_hunks(file_lines: list[str]) -> list[Hunk]:
    """Parse hunks from the given file lines. Each hunk starts with an @@ line."""
    hunks = []
    i = 0
    while i < len(file_lines):
        match = hunk_header_re.match(file_lines[i])
        if match:
            old_start, old_length, new_start, new_length = parse_hunk_header(match)
            i += 1
            # Collect hunk lines until next hunk or end of file
            hunk_lines = []
            while i < len(file_lines) and not hunk_header_re.match(file_lines[i]) and not file_header_old_re.match(file_lines[i]) and not file_header_new_re.match(file_lines[i]):
                hunk_lines.append(file_lines[i])
                i += 1

            changes = parse_hunk_lines(hunk_lines, old_start, new_start)
            hunk = Hunk(
                old_start=old_start,
                old_length=old_length,
                new_start=new_start,
                new_length=new_length,
                changes=changes
            )
            hunks.append(hunk)
        else:
            i += 1
    return hunks


def parse_hunk_header(match: re.Match) -> tuple[int, int, int, int]:
    """Parse a hunk header line match to get old_start, old_length, new_start, and new_length."""
    old_start = int(match.group(1))
    old_length_str = match.group(2)
    new_start = int(match.group(3))
    new_length_str = match.group(4)

    old_length = int(old_length_str) if old_length_str.isdigit() else 1
    new_length = int(new_length_str) if new_length_str.isdigit() else 1
    return old_start, old_length, new_start, new_length


def parse_hunk_lines(hunk_lines: list[str], old_start: int, new_start: int) -> list[Lines]:
    """Parse individual lines in a hunk."""
    changes: list[Lines] = []
    old_line_number = old_start
    new_line_number = new_start

    for line in hunk_lines:
        if line.startswith(' '):
            changes.append(UnchangedLine(
                line=line[1:],
                old_line_number=old_line_number,
                new_line_number=new_line_number
            ))
            old_line_number += 1
            new_line_number += 1
        elif line.startswith('-'):
            changes.append(RemovedLine(
                line=line[1:],
                line_number=old_line_number
            ))
            old_line_number += 1
        elif line.startswith('+'):
            changes.append(AddedLine(
                line=line[1:],
                line_number=new_line_number
            ))
            new_line_number += 1
    return changes

def process_diff(diff_string: str) -> UnifiedDiff | None:
    """Master function orchestrating parsing of the unified diff."""
    lines = diff_string.splitlines()
    results = {"files": []}

    i = 0
    while i < len(lines):
        file_header = parse_file_headers(lines, i)
        if file_header is None:
            i += 1
            continue

        old_file, new_file, next_index = file_header
        # Gather lines for this file until next file or end
        file_block = []
        i = next_index
        while i < len(lines):
            if file_header_old_re.match(lines[i]):
                # next file starts here
                break
            file_block.append(lines[i])
            i += 1

        hunks = parse_hunks(file_block)
        if hunks:
            results["files"].append({
                "old_file": old_file,
                "new_file": new_file,
                "hunks": [h.model_dump() for h in hunks]
            })

    if not results["files"]:
        # No diff content found
        return None

    # Validate with Pydantic
    unified_diff = UnifiedDiff(**results)
    return unified_diff
