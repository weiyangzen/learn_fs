# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/unlink.rs

## Purpose
This file defines performance counter scenarios for `unlink`, focusing on removing files and symlinks, missing-name failure, directory-type failure, nested path overhead, and deletion of large file/symlink payloads.

## Important APIs, Types, and Functions
The `unlink` group includes twelve scenarios. Counted operations call `fixture.filesystem.unlink(parent, PathComponent)`. Setup uses `create_file`, `create_symlink`, `mkdir`, `mkdir_recursive`, `create_and_open_file`, `write`, and `release`. Large cases use `NUM_BYTES_FOR_THREE_LEVEL_TREE` and `NumBytes` to write a file or create a long symlink target large enough to span multiple nodes.

## Control Flow
Success cases create a file or symlink in setup and remove it during the counted phase. Missing and directory cases assert errors. Nested and deeply nested cases return the parent node handle from setup, then unlink by child name. Large file setup writes and releases a large file before the counted unlink; large symlink setup creates a long target, then unlinks it.

## State and Persistence Behavior
Successful unlink updates the parent directory blob, flushes changes, and removes the target's backing storage. Large file and large symlink removal also delete subordinate high-level/low-level blocks, shown by `store_remove_by_id` and low-level `remove` counts. Directory unlink failure may still mutate and flush metadata in current behavior, as reflected by write/resize/flush counts in directory failure scenarios.

## Dependencies and Integration Points
The file depends on the filesystem driver abstraction, test driver, path types, `NumBytes`, `FixtureType`, large-tree constants, and blobstore/blockstore action counters. It shares stress constants and behavior expectations with write, truncate, and symlink tests.

## Risks and Notes
Directory failure cases counting writes and flushes are notable risk areas because type-check ordering or atime updates could change them. Large file and long symlink deletion rely on similar block-removal counts, so block-tree layout changes could alter both. Several count blocks are marked TODO.

## Test Signals
The file validates successful file and symlink unlink, ENOENT-like failure, EISDIR-like failure, path-depth overhead for fuser/fuse-mt, and cleanup of multi-block data. Exact count equality acts as a regression signal for storage lifecycle behavior.
