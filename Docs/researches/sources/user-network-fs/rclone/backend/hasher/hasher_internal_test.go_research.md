# sources/user-network-fs/rclone/backend/hasher/hasher_internal_test.go

## Purpose
This internal test file checks hasher behavior when uploading from a crypt remote, especially whether the hasher can generate and cache a checksum for content whose wrapped source may not expose the target hash directly.

## Important APIs, Types, And Control Flow
`putFile` writes a test object with fixed mtime. `testUploadFromCrypt` creates a temporary local remote, wraps it with an in-memory crypt remote, uploads a small file, prunes any existing hasher cache record, verifies the raw hash is absent, uploads from crypt into the hasher remote, and then checks that a hash record exists when caching is enabled. It purges the test directory afterward. `InternalTest` skips on unsupported kv platforms and runs the subtest.

## State And Persistence
The test creates a temporary local filesystem tree and removes it afterward. It mutates the hasher kv cache by pruning and then expecting a new hash record. Remote test data is purged through rclone operations.

## Dependencies And Integration Points
It uses crypt backend syntax, password obscuring, `fs.NewFs`, generic `fstests.PutTestContents`, operations purge, and hasher raw hash helpers from adjacent package files. It runs through the `fstests.InternalTester` hook.

## Risks And Test Signals
The test specifically guards upload-from-crypt hash capture and disabled-cache behavior. It depends on kv support and the crypt backend being importable through the test environment.
