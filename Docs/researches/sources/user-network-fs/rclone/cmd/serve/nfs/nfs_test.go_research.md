# sources/user-network-fs/rclone/cmd/serve/nfs/nfs_test.go

## Purpose

This small Unix-only test verifies that NFS can be started through rclone's generic RC serve mechanism.

## Important APIs, Types, and Functions

`TestRc` calls `servetest.TestRc` with `type: nfs` and `vfs_cache_mode: off`.

## Control Flow

The serve test harness creates the service through RC parameters and validates the standard serve handle behavior.

## State and Persistence Behavior

The test relies on harness-managed temporary state and does not persist NFS cache state directly.

## Dependencies and Integration Points

It depends on the local backend, `servetest`, RC params, and Unix build tag.

## Risks and Test Signals

It is a smoke test only. Actual NFS protocol behavior is covered by cache/handler tests here and more complete serving tests referenced in `cmd/nfsmount`.
