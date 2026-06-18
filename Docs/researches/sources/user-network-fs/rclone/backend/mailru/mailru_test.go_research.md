# sources/user-network-fs/rclone/backend/mailru/mailru_test.go

## Purpose
`mailru_test.go` wires the Mail.ru backend into rclone's shared backend integration suite. It does not define local unit tests; its role is to ensure the full `mailru` `fs.Fs` and `fs.Object` implementation conforms to rclone's common filesystem contract when a configured `TestMailru:` remote is available.

## Important APIs, Types, And Functions
The only test function is `TestIntegration`. It calls `fstests.Run` with `fstests.Opt{RemoteName: "TestMailru:", NilObject: (*mailru.Object)(nil), SkipBadWindowsCharacters: true}`. `NilObject` tells the shared harness the concrete object type expected from the backend. `SkipBadWindowsCharacters` acknowledges Mail.ru or the backend encoding behavior around names that are problematic on Windows-like filesystems.

## Control Flow
At test runtime, rclone's integration harness reads the named remote from test configuration, constructs the backend through `mailru.NewFs`, and runs the standard operation matrix: object creation, listing, metadata, reads, updates, moves, removals, directory behavior, optional interfaces, and error behavior. The file itself simply delegates into that harness.

## State And Persistence Behavior
The test uses a real or configured test remote and therefore mutates remote Mail.ru state under the harness-controlled test root. There is no file-local state, fixture, or cleanup logic; `fstests.Run` owns setup and teardown.

## Dependencies And Integration Points
The file depends on `github.com/rclone/rclone/backend/mailru` and `github.com/rclone/rclone/fstest/fstests`. It is an integration point between backend-specific code and rclone's common backend contract tests.

## Risks And Edge Cases
Coverage depends on credentials and service availability, so it may be skipped or fail for environmental reasons unrelated to code changes. Backend-specific paths such as OAuth reauthorization, speedup, binary listing quirks, server pool contention, and hash mismatch error handling are not explicitly isolated here.

## Test Signals
A passing run is a broad conformance signal for object lifecycle and optional interface behavior. Focused unit tests would still be useful for speedup pattern parsing, `mrhash` integration, binary list parsing, and error mapping.
