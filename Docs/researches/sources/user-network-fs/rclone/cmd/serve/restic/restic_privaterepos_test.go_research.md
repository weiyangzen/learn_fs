<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_privaterepos_test.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/restic_privaterepos_test.go

Source read: complete file, 78 lines, 2802 bytes, sha256 `c5ca6ccdad4a72ff7d66802d1739ca19f1ee7650e9cc3ab4bbf59a5ed7cc02d5`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/restic_privaterepos_test.go_research.md`.

## Purpose
Tests `--private-repos` access control for restic serve.

## Important APIs, types, and functions
`newAuthenticatedRequest` wraps test request creation and Basic Auth. `TestResticPrivateRepositories` configures one valid user/password and checks allowed, unauthorized, and forbidden paths.

## Control flow
The test posts and gets under `/test/`, then retries with missing or bad credentials, then requests root and another user's prefix.

## State and persistence behavior
State is a temporary local Fs plus HTTP auth config on the test server. No persistent credentials are written.

## Dependencies and integration points
Depends on lib/http Basic Auth behavior, chi route parameters, and restic request helpers.

## Risks and edge cases
It validates only Basic Auth username matching; proxy/custom auth combinations are not covered here.

## Test signals
Signals that authenticated users can access only their matching repository prefix and all other paths are forbidden.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_privaterepos_test.go -->
