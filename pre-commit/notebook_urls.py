"""Simple check to ensure each code cell in a notebook is valid Python."""
import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Set


def git_branch_name() -> str:
    """Get the current branch name."""
    return (
        subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"])
        .decode()
        .strip()
    )


def git_branch_modified_paths() -> Set[Path]:
    """Get a set of file paths modified on this branch vs develop."""
    import os

    from_ref = (
        os.environ.get("PRE_COMMIT_FROM_REF")
        or os.environ.get("PRE_COMMIT_SOURCE")
        or "develop"
    )
    to_ref = (
        os.environ.get("PRE_COMMIT_TO_REF")
        or os.environ.get("PRE_COMMIT_ORIGIN")
        or git_branch_name()
    )
    from_to = (f"{from_ref}...{to_ref}",)
    return {
        Path(p)
        for p in subprocess.check_output(
            [
                "git",
                "diff",
                "--name-only",
                from_to,
            ]
        )
        .decode()
        .strip()
        .splitlines()
    }


def git_previous_commit_modified_paths() -> Set[Path]:
    """Get a set of file paths modified in the previous commit."""
    return {
        Path(p)
        for p in subprocess.check_output(["git", "diff", "--name-only", "HEAD~"])
        .decode()
        .strip()
        .splitlines()
    }


@dataclass(frozen=True)
class Replacement:
    pattern: str
    replacement: str
    main_replacement: str = None


MAIN_BRANCHES = ("master", "main")
GIT_REV = git_branch_name()
REPLACEMENTS = [
    Replacement(
        (
            r"(^\s*[!%]\s*)pip install "
            "(git+https://github.com/TissueImageAnalytics/tiatoolbox.git@.*|tiatoolbox)"
        ),
        (
            r"\1pip install "
            f"git+https://github.com/TissueImageAnalytics/tiatoolbox.git@{GIT_REV}"
        ),
        r"\1pip install tiatoolbox",
    ),
]


def main(files: List[Path]) -> bool:
    """Check that URLs in the notebook are relative to the current branch."""
    passed = True
    modified_paths = git_branch_modified_paths().union(
        git_previous_commit_modified_paths()
    )
    for path in files:
        if path not in modified_paths:
            continue
        print(path)
        file_changed = False
        # Load the notebook
        with open(path, encoding="utf-8") as fh:
            notebook = json.load(fh)
        # Check each cell
        for cell_num, cell in enumerate(notebook["cells"]):
            # Check each line
            for line_num, line in enumerate(cell["source"]):
                new_line = replace_line(line)
                if new_line != line:
                    print(
                        f"{path.name}: Changed (cell {cell_num+1}, line {line_num+1})"
                    )
                    file_changed = True
                    passed = False
                    cell["source"][line_num] = new_line
        # Write the file if it has changed
        if file_changed:
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(notebook, fh, indent=1, ensure_ascii=False)
                fh.write("\n")
    return passed  # noqa: R504


def replace_line(line: str) -> str:
    """Perform pattern replacements in the line."""
    for r in REPLACEMENTS:
        if re.match(r.pattern, line):
            # Replace matches
            if GIT_REV in MAIN_BRANCHES:
                line = re.sub(r.pattern, r.main_replacement, line)
            else:
                line = re.sub(r.pattern, r.replacement, line)
            print(line)
    return line


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check notebook URLs")
    parser.add_argument("files", nargs="+", help="Path to notebook(s)", type=Path)
    args = parser.parse_args()
    sys.exit(1 - main(args.files))
