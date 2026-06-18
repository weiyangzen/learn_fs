# sources/user-network-fs/rclone/backend/memory/memory_internal_test.go

## Purpose
`memory_internal_test.go` provides backend-specific internal tests for the memory backend. Its current focus is a regression test for purge/list deadlocks when the backend's native `Purge` feature is disabled and rclone falls back to listing and removing entries.

## Important APIs, Types, And Functions
`InternalTest` implements `fstests.InternalTester` for `*Fs` and registers the `PurgeListDeadlock` subtest. `testPurgeListDeadlock` creates a test run, makes the remote root, disables the backend `Purge` feature, writes 100 small objects, and calls `operations.Purge`.

## Control Flow
The shared fstest harness can detect and call `InternalTest`. The deadlock test forces the fallback purge path by disabling the optional feature, then creates enough files that listing and removal overlap meaningfully. The memory backend's `ListR` implementation collects entries before invoking callbacks; this test protects that design choice.

## State And Persistence Behavior
The test uses the memory backend's process-global bucket state through `fstest.NewRunIndividual`. It creates transient objects with a fixed test timestamp and relies on the harness for cleanup/isolation.

## Dependencies And Integration Points
The file imports the local backend package, local backend registration for comparison support, `operations.Purge`, `fstest`, `fstests`, and `testify/require`. It asserts the memory backend implements `fstests.InternalTester`.

## Risks And Edge Cases
The test detects gross deadlock by completion, but it does not assert final empty state or run under explicit timeout in this file. Because the memory backend is global, poor harness isolation could make object counts or bucket names interact with other tests.

## Test Signals
Passing confirms fallback purge can list and delete many files without locking itself. It specifically supports the `ListR` implementation comment that calling `list.Add` while holding the bucket read lock could deadlock.
