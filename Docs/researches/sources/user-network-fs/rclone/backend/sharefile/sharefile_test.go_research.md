# sources/user-network-fs/rclone/backend/sharefile/sharefile_test.go

## Purpose

This file wires the ShareFile backend into rclone's generic integration test suite. It verifies the backend through the common `fstests` contract rather than backend-local unit tests.

## Important APIs, Types, and Functions

`TestIntegration` calls `fstests.Run` with `RemoteName: "TestSharefile:"`, `NilObject: (*Object)(nil)`, and a `ChunkedUploadConfig` using the backend's `minChunkSize` and `fstests.NextPowerOfTwo` chunk-size ceiling. Test-only methods `SetUploadChunkSize` and `SetUploadCutoff` expose the unexported setters used by generic upload tests. Interface assertions require `*Fs` to satisfy `fstests.SetUploadChunkSizer` and `fstests.SetUploadCutoffer`.

## Control Flow

The test harness discovers configuration for `TestSharefile:`, constructs the backend, then executes standard object, directory, move/copy, hash, purge, and chunked upload scenarios. The chunk-size setter lets the harness force boundary sizes and confirm the backend reinitializes its upload buffer token pool.

## State and Persistence Behavior

The file has no persistent state. It does mutate backend upload options during integration tests through the exposed setters, and those changes are confined to the in-memory `Fs` under test.

## Dependencies and Integration Points

It depends on `github.com/rclone/rclone/fstest/fstests` and the backend package itself. The strongest integration signal is conformance to rclone's common remote filesystem behavior against a live ShareFile account.

## Risks and Edge Cases

These are live integration tests and require valid remote configuration and network access. They do not unit-test ShareFile error parsing, timezone correction, or copy/move workaround branches directly. The test-only setters are compiled with the package and must remain consistent with internal validation.

## Test Signals

Success indicates the backend satisfies rclone's generic filesystem expectations, including chunked upload behavior. Failures around chunk sizes, modtimes, or move/copy operations usually point back to `sharefile.go` and `upload.go`.
