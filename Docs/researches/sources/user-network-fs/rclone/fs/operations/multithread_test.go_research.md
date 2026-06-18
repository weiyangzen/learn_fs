# sources/user-network-fs/rclone/fs/operations/multithread_test.go

## Purpose
`multithread_test.go` validates the decision logic, chunk calculation, end-to-end chunked copy behavior, metadata handling, and abort safety for `multithread.go`.

## Important APIs, types, and functions
- `TestDoMultiThreadCopy` unit-tests feature/config eligibility.
- `TestMultithreadCalculateNumChunks` validates ceiling division.
- `skipIfNotMultithread` gates integration tests and probes backend chunk size.
- `TestMultithreadCopy` copies data across local/remote directions at chunk-boundary sizes.
- `errorObject`, `errorReadCloser`, and `wgReadCloser` simulate late ranged-read failure.
- `TestMultithreadCopyAbort` verifies abort does not overwrite or leave the wrong destination state.

## Control flow
The eligibility test constructs mock filesystems and toggles config and feature flags. The integration test probes chunk size, creates content with sizes just below, equal to, and above two chunks, alternates upload/download direction, optionally sets metadata on sources, calls `multiThreadCopy` directly with a transfer, and verifies listings, sizes, paths, metadata, and cleanup. The abort test writes a canary destination, then wraps the source so the final ranged read fails after earlier chunks start.

## State and persistence behavior
Tests create temporary local/remote files, toggle global multi-thread config fields and restore them, temporarily restrict hashes for local backend performance, create and abort multipart or writer-at uploads, and reset accounting counters. They remove copied source/destination objects after successful copy scenarios.

## Dependencies and integration points
The tests use mock fs/object packages, `fs`, `accounting`, `hash`, `object.NewStaticObjectInfo`, `fstest`, random content, synchronization primitives, and `testify`. They exercise internal unexported functions because the test package is `operations`.

## Risks and edge cases
Backends may skip because they lack chunk writers or because a probe file is too small for multipart upload. Size limits can skip large transfer cases. Abort expectations differ when a backend uses partial uploads versus direct overwrite semantics. The simulated read failure coordinates chunks with a wait group to ensure failure happens after some chunks have begun.

## Test signals
The tests confirm multi-threading is disabled for too few streams, small files, unsupported destinations, local/local defaults, or source opt-out; enabled when explicitly requested and supported; chunk counts are correct; copied files preserve size/modtime/listing and sometimes metadata; and failed chunk copies do not silently replace a canary destination.
