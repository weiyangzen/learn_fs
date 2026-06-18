<!-- BEGIN_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check_translation_update.py -->
# sources/test-tools/syzkaller/tools/check_translation_update.py

## Purpose

Translation freshness checker for `docs/translations` based on source commit markers in translation commit messages.

## Important APIs, Types, and Functions

Functions include `get_git_repo_root`, `get_latest_commit_info`, `extract_source_commit_info`, `extract_translation_language`, `check_translation_update`, `extract_compact_date`, and `main`; shells out to `git` through `subprocess.run`.

## Control Flow

Finds repo root, walks translations or checks `--files`, skips README/non-translation paths, parses `Update to commit HASH ("TITLE")` from latest translation commit, maps translation path to source doc, compares commit prefixes, and prints summary counts.

## State and Persistence Behavior

Reads Git history and files; no writes; exits 0 currently even for stale translations.

## Dependencies and Integration Points

Requires Python, Git history, and mirrored `docs/translations/<lang>/...` layout.

## Risks and Edge Cases

Shallow clones and malformed commit messages reduce coverage; source path mapping is convention-based; stale translations are informational until exit codes change.

## Test Signals

Temporary git repo fixtures for matching, stale, missing-marker, missing-source, and explicit `--files` cases.
<!-- END_FILE_RESEARCH: sources/test-tools/syzkaller/tools/check_translation_update.py -->
