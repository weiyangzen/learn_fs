# sources/user-network-fs/rclone/backend/internetarchive/internetarchive_test.go

## Purpose
Defines the Internet Archive backend integration test entrypoint.

## Important APIs, Types, and Functions
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestIA:lesmi-rclone-test/"` and `NilObject: (*internetarchive.Object)(nil)`.

## Control Flow
The test delegates all behavior to rclone's common integration suite against a configured IA item path.

## State and Persistence
The file stores no state. Remote IA test state is managed by the generic test suite and IA's backend behavior.

## Dependencies and Integration Points
Imports the backend and rclone `fstests`. It is the main configured-service regression signal for the IA backend.

## Risks and Edge Cases
Because IA write/delete visibility is asynchronous unless `wait_archive` is configured, integration tests can be sensitive to remote processing delays. Offline unit coverage is absent.

## Test Signals
Broad filesystem conformance can be checked when `TestIA:` credentials and item are available. Helper-level regressions require additional tests outside this file.
