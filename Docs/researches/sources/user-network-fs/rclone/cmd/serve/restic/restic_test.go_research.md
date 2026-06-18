<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_test.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/restic_test.go

Source read: complete file, 183 lines, 4633 bytes, sha256 `dea4ac732a540424c0918db769f126382938a8d3eabe817bfc1dce4b57217958`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/restic_test.go_research.md`.

## Purpose
Provides restic serve integration and handler error tests.

## Important APIs, types, and functions
`newOpt` creates localhost listener options. `TestResticIntegration` optionally runs upstream restic REST backend tests against a live rclone server. `TestMakeRemote`, `TestListErrors`, `TestServeErrors`, and `TestRc` cover path rewriting, error mapping, and rc registration.

## Control flow
The integration test starts a temporary remote-backed server, changes into an external restic source tree, and runs `go test` with `RESTIC_TEST_REST_REPOSITORY`. Unit-style tests invoke the router directly.

## State and persistence behavior
State includes temporary remote content, process working directory changes during upstream tests, and test server listeners. Error wrapper Fs types inject list/NewObject failures.

## Dependencies and integration points
Depends on restic source checkout availability, rclone backend/all imports, servetest, httptest, and rc.

## Risks and edge cases
The integration test is skipped if the restic source tree is absent and mutates cwd, so cleanup correctness matters. Error tests cover HTTP status mapping but not all backend error classes.

## Test signals
Signals compatibility with restic's external server tests when available and deterministic behavior for URL-to-remote mapping and common errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_test.go -->
