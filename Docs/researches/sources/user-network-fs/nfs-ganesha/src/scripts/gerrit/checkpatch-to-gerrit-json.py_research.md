# sources/user-network-fs/nfs-ganesha/src/scripts/gerrit/checkpatch-to-gerrit-json.py

## Purpose

This filter converts `checkpatch.pl` output into Gerrit review JSON comments.

## Important APIs, Types, and Functions

Top-level code reads stdin in groups containing a message and `FILE: path:line:` marker, accumulates `comments` keyed by file, and prints a JSON object with either `comments` and a summary message or `Checkpatch OK`.

## Control Flow

The script repeatedly reads a first line and file-line, stops when the file-line is blank, then appends continuation lines until a blank separator. It extracts filename and line with regex and appends comment dictionaries. At the end it emits JSON to stdout.

## State and Persistence Behavior

Only an in-memory `comments` dict is maintained. There is no persistence.

## Dependencies and Integration Points

It depends on Python `json`, `re`, and `sys`. `gerrit-checkpatch.sh` pipes `checkpatch.pl` output through it into `gerrit review --json`.

## Risks and Edge Cases

The script uses `comments.has_key`, invalid in Python 3, while the shebang is generic `python`. It assumes every issue has a matching `FILE:` line; malformed input can make `filere` `None`. It does not include labels, only comments/message.

## Test Signals

Feed sample checkpatch outputs with one issue, multiple issues per file, multiple files, and no issues. Run under both Python 2 expectations and the repository's supported Python 3 environment to catch `has_key`.
