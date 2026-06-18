<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_utils_test.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/restic_utils_test.go

Source read: complete file, 53 lines, 1491 bytes, sha256 `9fe21efdaf8f93ba0371b405275b3772a38b18591626a9daa96c5724d0ac1d85`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/restic_utils_test.go_research.md`.

## Purpose
Defines shared HTTP test helpers for restic serve tests.

## Important APIs, types, and functions
`wantFunc`, `newRequest`, `wantCode`, `wantBody`, `checkRequest`, and `TestRequest` make handler tests concise and ensure the restic v2 Accept header is present.

## Control flow
Tests build httptest requests, route them through a handler, and apply a list of response assertions.

## State and persistence behavior
No persistent state. Helpers create request/recorder objects only.

## Dependencies and integration points
Depends on `httptest`, `net/http`, `io`, and testify assertions.

## Risks and edge cases
The helpers compare body bytes exactly and do not close request bodies, appropriate for httptest but not a production pattern.

## Test signals
Used by append-only, private-repo, list-error, and serve-error tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_utils_test.go -->
