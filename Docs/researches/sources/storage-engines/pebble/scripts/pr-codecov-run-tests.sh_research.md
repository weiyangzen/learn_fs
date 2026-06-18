# sources/storage-engines/pebble/scripts/pr-codecov-run-tests.sh

## Purpose
This script runs coverage-enabled tests for a caller-provided list of package paths and converts the result to JSON for PR code coverage workflows.

## Important APIs, Types, and Functions
Arguments are `output_json_file` and a space-separated `packages` string. It checks each package path for Go files, normalizes non-root paths to `./path`, runs `make testcoverage COVER_PROFILE=... PKG=...`, and converts with `gocover2json@v1.0.0`.

## Control Flow
It builds a valid path list, skips with an empty output file if no packages exist in the current checkout, creates a temporary coverprofile, runs coverage, converts to JSON, and removes the temp file on exit.

## State and Persistence Behavior
It writes the requested JSON file and a temporary coverage profile.

## Dependencies and Integration Points
It depends on Bash, `ls`, `mktemp`, `make testcoverage`, Go, and CockroachDB code coverage utilities. It tolerates package paths not present in the checkout, which is useful for PR diffs across branches.

## Risks
Package splitting uses shell word splitting, so paths with whitespace are unsupported. Missing packages are silently skipped. Conversion requires module/network availability unless cached.

## Test Signals
The JSON output is the primary artifact. Empty touched output means no valid packages were found.
