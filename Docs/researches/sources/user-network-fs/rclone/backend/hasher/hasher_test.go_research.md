# sources/user-network-fs/rclone/backend/hasher/hasher_test.go

## Purpose
This file wires hasher into rclone's generic filesystem integration suite.

## Important APIs, Types, And Control Flow
`TestIntegration` skips when kv is unsupported. It builds `fstests.Opt` with the configured remote or, when no remote is supplied, creates a temporary local-backed `TestHasher` remote. It marks `OpenWriterAt` and `OpenChunkWriter` unimplementable, runs the generic suite, then runs it again with `max_age=0` to test disabled cache mode.

## State And Persistence
Default test state uses a temp directory under the OS temp path and may create a hasher kv DB depending on `max_age`. The second run intentionally disables persistent cache records.

## Dependencies And Integration Points
It imports all rclone backends for integration tests, the production hasher package, `fstest`, `fstests`, and `kv`.

## Risks And Test Signals
The tests provide broad rclone interface coverage for both cached and no-cache modes, but they depend on generic suite behavior for most assertions. Specific command/import/dump behavior is not covered here.
