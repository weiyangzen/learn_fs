# sources/test-tools/kdevops/scripts/github_output.sh

## Purpose
This GitHub Actions helper appends a `key=value` pair to the path in `$GITHUB_OUTPUT`, which is the modern workflow mechanism for setting step outputs.

## Important APIs, Types, And Functions
There are no functions. It expects exactly two positional arguments: `key="$1"` and `value="$2"`. It runs with `set -euxo pipefail`, so missing arguments, unset `GITHUB_OUTPUT`, and failed writes abort.

## Control Flow
The script assigns the first two positional parameters and appends a single line using `echo "$key=$value" >> "$GITHUB_OUTPUT"`.

## State And Persistence
The persistent side effect is appending to the file named by `GITHUB_OUTPUT`. It does not validate or sanitize the key or value and does not handle multiline GitHub output syntax.

## Dependencies And Integration Points
It integrates directly with GitHub Actions. The surrounding workflow must set `GITHUB_OUTPUT`, pass safe single-line values, and ensure the output file is writable.

## Risks And Test Signals
Values containing newlines, percent-like content, or names that collide with other step outputs can create ambiguous workflow output. `set -x` may echo sensitive values in CI logs. Tests should run with a temporary `GITHUB_OUTPUT`, verify append semantics, and cover missing arguments/unset environment behavior.
