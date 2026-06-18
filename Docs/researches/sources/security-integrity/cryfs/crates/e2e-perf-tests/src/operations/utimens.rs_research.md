# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/utimens.rs

## Purpose
This file defines performance counter scenarios for updating timestamps with `utimens` on files, directories, and symlinks in root and nested locations.

## Important APIs, Types, and Functions
The `utimens` group includes `file_in_rootdir`, `dir_in_rootdir`, `symlink_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir`. Each counted operation calls `fixture.filesystem.utimens(Some(node), Some(atime), Some(mtime))` with fixed `SystemTime` values derived from `UNIX_EPOCH` plus `Duration`.

Setup creates targets through `create_file`, `mkdir`, `create_symlink`, and `mkdir_recursive`. Counts vary by `FixtureType`, especially for nested and deeply nested paths.

## Control Flow
Each scenario creates one target node in setup, then the counted phase constructs deterministic atime and mtime values and calls `utimens`. The test unwraps success and asserts exact storage operation counts.

## State and Persistence Behavior
`utimens` mutates metadata stored in the target node. File cases generally avoid full blob reads with inode cache, while directory and symlink cases read all blob data because their metadata/content access pattern differs. The operation writes and resizes the blob metadata area and stores a low-level block. Nested file cases show additional loads and reads for path reconstruction when no inode cache is available.

## Dependencies and Integration Points
The file depends on `std::time`, CryFS path types, the filesystem driver abstraction, test-driver builder, `FixtureType`, and the action-count structures. It integrates with macro-generated atime behavior variants, although the operation itself supplies explicit atime/mtime values and does not branch on the atime mode.

## Risks and Notes
Counts encode timestamp metadata serialization details and lookup-cache behavior. If timestamp storage moves, metadata blob layout changes, or symlink timestamp semantics change, the expected read/write profile will need revision.

## Test Signals
The tests signal that timestamp updates are one-node metadata mutations, while still distinguishing file, directory, and symlink storage access patterns and root/nested/deep lookup overhead.
