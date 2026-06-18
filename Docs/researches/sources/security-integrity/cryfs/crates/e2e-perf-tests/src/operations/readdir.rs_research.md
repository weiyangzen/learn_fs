# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/readdir.rs

## Purpose
This file defines performance counter tests and benchmarks for directory listing. It covers an empty root, a populated root, populated nested and deeply nested directories, and a large directory with enough entries to force multi-block directory storage.

## Important APIs, types, and functions
- Registers `empty_rootdir`, `rootdir_with_entries`, `nesteddir`, `deeplynesteddir`, and `large_directory`.
- Uses `FilesystemDriver::readdir` as the measured operation.
- Setup uses `mkdir`, `mkdir_recursive`, `create_file`, and `create_symlink` to populate directories.
- Uses `NUM_BYTES_FOR_THREE_LEVEL_TREE / BLOCKID_LEN` to choose a large directory entry count.
- Computes directory atime updates from `AtimeUpdateBehavior`, where `Noatime`, `NodiratimeRelatime`, and `NodiratimeStrictatime` skip directory atime writes.

## Control flow
Root cases call `readdir(None)`. Nested cases create a parent directory, populate it with a directory, file, and symlink, then call `readdir(Some(handle))`. The large-directory case creates `large_dir`, inserts many files under it, and reads that directory. Expected counts are fixture-specific and add atime write/resize/store costs where directory atime should change.

## State and persistence behavior
Readdir is primarily a read of the directory blob plus loads of child metadata needed to produce entries. For non-root directory reads, some atime policies update the directory blob, adding blob writes/resizes and low-level stores. The large-directory case persists enough entries during setup to require a multi-level backing structure, making the measured read show high `HLActionCounts::store_load` and `LLActionCounts::load` values.

## Dependencies and integration points
The file integrates with the same `TestDriver` harness and all fixture types. It uses `AtimeUpdateBehavior` directly rather than treating atime as uniform. The expected counts also depend on the directory encoding and on whether the filesystem driver caches inode/node resolution.

## Risks and observations
Many expected counts are marked for review. The operation registry notes a broader suspicion that atime behavior does not affect all operations as expected; this file is one of the suites where atime does affect counts for nested directory reads. Large-directory counts are especially brittle because they depend on test constants, block-id length, and directory tree layout.

## Test signals
The suite checks that empty root listing costs one root load/read; populated root listing loads child metadata; nested/deeply nested reads scale with lookup depth and fixture type; directory atime policies add exactly one timestamp write path; and a large directory triggers substantially more high-level and low-level loads.
