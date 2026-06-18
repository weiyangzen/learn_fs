# sources/user-network-fs/rclone/backend/smb/filepool_test.go

## Purpose

This file unit-tests the SMB `filePool` helper with a mocked backend interface.

## Important APIs, Types, and Functions

`mockFs` implements `FsInterface` and records whether `getConnection`, `putConnection`, and `removeSession` were called. `newMockFile` returns a `file` with zero-value SMB objects. Tests cover `newFilePool`, `filePool.get`, `filePool.put`, `filePool.drain`, and concurrent access.

## Control Flow

Tests seed the pool directly or configure mock errors, then call pool methods and assert internal state or mock call records. `TestFilePool_ConcurrentAccess` preloads ten files, runs ten goroutines that get and put handles, waits on a channel, and asserts the pool length returns to ten.

## State and Persistence Behavior

All state is local test memory. There are no network calls because the mock either returns an error or a dummy `conn`.

## Dependencies and Integration Points

It uses `testify/assert`, `context`, `sync`, and `go-smb2` types. It tests `filepool.go` in package `smb`, so it can access unexported types.

## Risks and Edge Cases

The tests do not exercise successful empty-pool opens because that would require a real `smbShare`. `drain` ignores possible close behavior of real SMB files. Assertions mostly validate pool bookkeeping rather than actual SMB semantics.

## Test Signals

Passing tests signal mutex-protected pool bookkeeping and error routing are stable. Race-detector runs are useful for the concurrent test.
