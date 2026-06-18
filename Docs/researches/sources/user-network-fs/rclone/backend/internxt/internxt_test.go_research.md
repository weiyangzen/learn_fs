# sources/user-network-fs/rclone/backend/internxt/internxt_test.go

## Purpose
Defines the Internxt backend integration test entrypoint and configures rclone's shared test suite to exercise chunked uploads.

## Important APIs, Types, and Functions
`TestIntegration` calls `fstests.Run` with `RemoteName: "TestInternxt:"` and `ChunkedUpload` config requiring 100 MiB minimum chunk size and multiple chunks.

## Control Flow
When a real `TestInternxt:` remote is configured, the generic suite exercises object and directory behavior, including multipart upload paths large enough to require multiple chunks.

## State and Persistence
No test-local persistence. Remote files/folders are managed by the shared integration framework.

## Dependencies and Integration Points
Uses rclone `fs` for size constants and `fstests` for the common test suite. It is the only explicit test file for Internxt in this subset.

## Risks and Edge Cases
The integration test requires account credentials, enough quota, and network availability. It does not provide deterministic offline coverage for auth refresh, rollback, conflict recovery, or single-part upload behavior.

## Test Signals
The chunked upload settings are an important signal that multipart behavior is expected to work and is part of backend conformance.
