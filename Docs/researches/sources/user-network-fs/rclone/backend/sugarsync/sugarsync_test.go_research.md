# sources/user-network-fs/rclone/backend/sugarsync/sugarsync_test.go

## Purpose

This file runs rclone's generic integration test suite against a SugarSync remote.

## Important APIs, Types, and Functions

`TestIntegration` calls `fstests.Run` with `RemoteName: "TestSugarSync:Test"` and `NilObject: (*sugarsync.Object)(nil)`.

## Control Flow

The generic suite creates the backend from the configured remote and exercises standard file and directory operations. The remote path includes `Test` to avoid known SugarSync limitations around moving root sync folders.

## State and Persistence Behavior

The file has no local state. The integration suite creates and removes remote SugarSync data under the configured test path.

## Dependencies and Integration Points

It imports the backend externally and depends on `fstests` plus valid SugarSync test credentials/tokens.

## Risks and Edge Cases

Live API availability and account state affect results. The generic suite may not fully cover auth refresh, soft-delete recovery semantics, or public-link behavior.

## Test Signals

Passing tests signal conformance to rclone's common backend behavior for SugarSync under the chosen test root.
