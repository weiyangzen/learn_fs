# sources/user-network-fs/rclone/backend/memory/memory_test.go

## Purpose
`memory_test.go` runs rclone's standard backend integration tests against the in-memory backend. It validates the memory backend as both a normal backend implementation and a fast test fixture.

## Important APIs, Types, And Functions
`TestIntegration` calls `fstests.Run` with `RemoteName: ":memory:"`, `NilObject: (*Object)(nil)`, and `QuickTestOK: true`. The package is `memory`, not `memory_test`, so it can pair with internal tests and access local types directly.

## Control Flow
The shared harness constructs a memory remote using connection string syntax, performs object and directory operations, and can run in quick-test mode because the backend is local and fast.

## State And Persistence Behavior
The test uses the backend's process-global `buckets` map. The harness is expected to create isolated test roots and clean them up, but no file-local cleanup exists.

## Dependencies And Integration Points
It imports `fstests` and uses the memory backend registration from the same package. It is the broad contract test complement to `memory_internal_test.go`.

## Risks And Edge Cases
Standard integration coverage may not stress discard mode, global-state collisions, or race behavior. Because the backend is memory-only, it may pass operation patterns that network backends fail under latency or eventual consistency.

## Test Signals
Passing indicates compatibility with rclone's common Fs/Object expectations, including put, list, read, update, remove, hashes, modtime, and optional interface behavior.
