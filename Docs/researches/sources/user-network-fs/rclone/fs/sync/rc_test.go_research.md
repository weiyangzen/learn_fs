# sources/user-network-fs/rclone/fs/sync/rc_test.go

## Purpose
This file tests the RC wrappers for sync, copy, and move directory operations.

## Important APIs, Types, and Functions
- `rcNewRun` creates a local fstest run, obtains the registered RC call, and inserts local/remote filesystems into `cache`.
- `TestRcCopy`, `TestRcMove`, and `TestRcSync` each prepare source/destination file sets, call the RC method, and assert final contents.

## Control Flow
Tests skip non-local remote test configurations, create source/destination files, call `call.Fn` with `srcFs` and `dstFs`, require no error, and verify copy/move/sync semantics: copy preserves extra destination files, move empties source, sync deletes destination-only files.

## State and Persistence
Tests create temporary local filesystem state via `fstest.Run` and mutate the global fs cache with `cache.Put` so RC filesystem resolution can find the test remotes.

## Dependencies and Integration Points
They depend on `fstest`, `fs/cache`, `rc.Calls`, and the actual sync engine. This is an integration-level test rather than a pure unit test.

## Risks and Edge Cases
The tests do not cover optional RC flags, invalid params, auth behavior, or remote backends with different capabilities. Cache mutation should remain test-isolated.

## Test Signals
The file confirms end-to-end RC registration and dispatch for the three primary directory operations on local backends.
