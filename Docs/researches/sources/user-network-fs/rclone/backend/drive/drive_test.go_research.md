# sources/user-network-fs/rclone/backend/drive/drive_test.go

## Purpose
This is the top-level Drive backend integration test entry point. It delegates to rclone's generic filesystem test suite with Drive-specific object type and chunked-upload settings.

## Important APIs, types, and functions
- `TestIntegration` calls `fstests.Run` with `RemoteName: "TestDrive:"`, `NilObject: (*Object)(nil)`, and a `ChunkedUploadConfig` using Drive's `minChunkSize` and `fstests.NextPowerOfTwo`.
- `SetUploadChunkSize` and `SetUploadCutoff` expose Drive's private setters to the generic test harness.
- Interface assertions ensure `*Fs` implements `fstests.SetUploadChunkSizer` and `fstests.SetUploadCutoffer`.

## Control flow
When integration tests run, `fstests.Run` constructs the `TestDrive:` remote, exercises standard rclone filesystem semantics, and uses the setter hooks to vary upload chunk and cutoff behavior. The actual backend behavior under test lives in `drive.go` and `upload.go`.

## State and persistence behavior
The test suite creates, updates, lists, moves, copies, and deletes objects on the configured Drive test remote. The setters mutate in-memory upload settings on the active `Fs`, allowing tests to probe chunk size/cutoff boundaries without changing persistent config.

## Dependencies and integration points
The file depends on rclone's `fs` package and `fstest/fstests`. It integrates with Drive constants and methods from `drive.go` and uses upload behavior from `upload.go`.

## Risks and edge cases
- Requires a configured `TestDrive:` remote and live Google Drive access.
- Chunk size validation is important because Drive resumable uploads require power-of-two chunks at least `googleapi.MinUploadChunkSize`.
- Failures may reflect remote API quota or account state rather than deterministic local behavior.

## Test signals
The file is a broad conformance signal: it asserts the Drive backend satisfies rclone's standard filesystem contract and that chunked upload knobs can be controlled by the test framework.
