# sources/user-network-fs/rclone/backend/combine/combine_test.go

## Purpose
This file provides generic filesystem test coverage for the combine backend using rclone's shared `fstests` framework. It exercises combine over configured external remotes, temporary local directories, in-memory remotes, and a mixed setup.

## Important APIs, types, and functions
`unimplementableFsMethods` records optional rclone features not expected from combine in these tests: `UnWrap`, `WrapFs`, `SetWrapper`, `UserInfo`, `Disconnect`, and `OpenChunkWriter`. `TestIntegration` uses a user-provided `fstest.RemoteName`. `TestLocal`, `TestMemory`, and `TestMixed` create combine configurations and call `fstests.Run`. `MakeTestDirs` creates temporary directories for local upstreams.

## Control flow
The external integration test is skipped unless `-remote` is configured. Local and memory tests are skipped when `-remote` is set. Each local-memory test builds an `upstreams` string such as `dir1=<path> dir2=<path> dir3=:memory:dir3`, registers a temporary config named `TestCombine...`, and tests a sub-root such as `TestCombineLocal:dir1`.

## State and persistence behavior
Local tests write to temp directories owned by the test process. Memory tests use rclone's memory backend. Mixed tests combine both. Cleanup is handled by Go temp directory cleanup and `fstests`. The combine backend itself persists nothing.

## Dependencies and integration points
The test imports local and memory backends for registration side effects, plus rclone `fstest` and `fstests`. It validates that combine can satisfy the shared rclone contract when backed by common upstreams.

## Risks and edge cases
The tests focus on a mounted subdirectory (`:dir1`) rather than exhaustive root-level multi-upstream behavior. They do not explicitly verify cross-upstream copy/move restrictions, quota aggregation, feature masking, change notification fan-out, purge across all upstreams, or metadata propagation. The external integration test depends on caller-supplied remote configuration.

## Test signals
The generic test suite provides broad operation coverage for object lifecycle, listings, hashes where available, and directory behavior. Combined with the internal adjustment tests, it gives useful confidence in common paths.
