# sources/user-network-fs/rclone/backend/storj/storj_test.go

## Purpose

This file connects the Storj backend to rclone's generic integration test suite on non-Plan 9 platforms.

## Important APIs, Types, and Functions

`TestIntegration` runs `fstests.Run` with `RemoteName: "TestStorj:"` and `NilObject: (*storj.Object)(nil)`.

## Control Flow

The generic suite builds the configured Storj remote and exercises standard rclone operations. Build tag `!plan9` matches the backend implementation files.

## State and Persistence Behavior

There is no local state beyond test execution. Remote buckets/objects are created and cleaned by the generic suite.

## Dependencies and Integration Points

It imports `backend/storj` externally as `storj_test` and depends on `fstests`. It requires a configured Storj test access grant.

## Risks and Edge Cases

Live Storj credentials and network are required. The generic suite may not cover public links or all bucket-creation retry behavior.

## Test Signals

Passing tests indicate core list, upload, read, update, delete, and directory behavior satisfy rclone contracts for Storj.
