# sources/user-network-fs/rclone/backend/imagekit/imagekit_test.go

## Purpose
Defines the ImageKit backend integration test entrypoint.

## Important APIs, Types, and Functions
`TestIntegration` sets `fstest.Verbose` to true and calls `fstests.Run` with `RemoteName: "TestImageKit:"`, `NilObject: (*Object)(nil)`, and `SkipFsCheckWrap: true`.

## Control Flow
When the test remote is configured, rclone's shared integration suite performs filesystem operations against ImageKit. `SkipFsCheckWrap` indicates the backend has behavior that should not be wrapped by the standard fs check layer.

## State and Persistence
No local state is persisted by the test file. Remote ImageKit state is created and cleaned by the integration suite.

## Dependencies and Integration Points
Imports rclone `fstest` and `fstests`. It is the only explicit test file for this backend.

## Risks and Edge Cases
No pure unit tests are provided for client validation, signed URL generation, list pagination, metadata mapping, or range handling. Integration tests require credentials and external service stability.

## Test Signals
The integration harness can catch broad API and interface regressions for configured developers/CI, but not small deterministic helper regressions in offline unit runs.
