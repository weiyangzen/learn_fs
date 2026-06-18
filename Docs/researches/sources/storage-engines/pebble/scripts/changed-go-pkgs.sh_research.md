# sources/storage-engines/pebble/scripts/changed-go-pkgs.sh

## Purpose
This small CI helper prints the unique directories containing Go files changed between a base SHA and head SHA, excluding `internal/devtools`.

## Important APIs, Types, and Functions
The script accepts `<base-sha> <head-sha>`, validates only that `HEAD_SHA` is non-empty, and uses `git diff --name-only`, `dirname`, `sort -u`, `grep -v`, and `xargs echo`.

## Control Flow
It exits with usage if the second argument is missing. Otherwise it diffs `BASE_SHA..HEAD_SHA` for `*.go`, maps files to directories, de-duplicates, filters devtools, and emits a space-separated package-directory list.

## State and Persistence Behavior
No persistent state is written. Output is derived from git history.

## Dependencies and Integration Points
It depends on git and standard Unix pipeline tools. It likely feeds CI package-selection or coverage scripts.

## Risks
If no Go files match, `xargs` behavior may still produce an empty line. It does not validate `BASE_SHA`, so git errors propagate through the pipeline only according to shell defaults because `set -euo pipefail` is not enabled.

## Test Signals
No direct tests are present; correctness is observable through CI package selection.
