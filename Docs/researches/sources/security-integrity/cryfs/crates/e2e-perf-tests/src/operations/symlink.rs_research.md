# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/symlink.rs

## Purpose
This file defines e2e performance counter scenarios for creating symbolic links. It measures creation in root, nested, and deeply nested directories, duplicate-name failure behavior, and a long target path that spans multiple storage nodes.

## Important APIs, Types, and Functions
The file registers `perf_test!(symlink, [...])` with seven scenarios: new and already-existing symlink creation from root, nested directory, and deeply nested directory, plus `long_target`. Scenarios use `fixture.filesystem.create_symlink(parent, name, &target)` with `PathComponent` link names and `AbsolutePath` targets.

Expected counts vary through `FixtureType` for path-depth cases. Long target setup uses `NUM_BYTES_FOR_THREE_LEVEL_TREE` to construct a repeated path string large enough to drive multi-block symlink content storage.

## Control Flow
For non-existing cases, setup prepares the target path and optionally creates the parent directory. The counted phase creates the symlink and unwraps success. Existing-name cases create the symlink during setup, reset cache/counters through the test driver, then attempt the same create again and require an error. The long-target case has no filesystem setup and creates a single symlink with a very large target string.

## State and Persistence Behavior
Successful symlink creation allocates a new blob/node for the symlink, updates the parent directory entry, writes target data, and flushes changed blocks. Duplicate creation attempts still create intermediate state in some paths and then remove it after discovering the name conflict, as shown by `store_create` paired with `store_remove` or `store_remove_by_id`. Long targets create many high-level blocks and low-level stores.

## Dependencies and Integration Points
The file depends on the filesystem test harness, `FixtureType`, `NUM_BYTES_FOR_THREE_LEVEL_TREE`, CryFS path types, and all three action-count structures. It integrates with `perf_test_macro.rs` for fuser/fuse-mt and atime expansion.

## Risks and Notes
Many count blocks are annotated as TODO. The duplicate-name behavior is especially sensitive: creating then removing storage before reporting an existing name may be an implementation detail rather than an inherent requirement. The path-depth branches encode current inode-cache behavior and may need updates if node handles or lookup caching change.

## Test Signals
The file verifies success and duplicate failure paths, root versus nested lookup overhead, deep path traversal costs, and the block allocation profile for long symlink targets. Counts include `exists`, `store_create`, `store_remove`, writes, flushes, and blob data mutations.
