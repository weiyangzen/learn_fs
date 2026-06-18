# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/rename.rs

## Purpose
This file defines e2e performance counter tests and benchmarks for renaming files, directories, and symlinks. It covers renames within one directory, across root/nested/deeply nested directories, replacing an existing target, and moving between shallow and deep directory trees.

## Important APIs, types, and functions
- Registers the main suite with `perf_test!` for `within_rootdir`, `between_nested_dirs`, `within_nested_dir`, `between_deeply_nested_dirs`, `to_existing_target`, `directory`, `symlink`, `from_nested_to_deeply_nested`, and `from_deeply_nested_to_nested`.
- Registers `from_rootdir_to_nesteddir` and `from_nesteddir_to_rootdir` separately with `perf_test_only_fusemt!` because running them across all fixtures currently deadlocks.
- Uses `FilesystemDriver::rename` as the measured operation, with setup through `create_file`, `mkdir`, `mkdir_recursive`, and `create_symlink`.
- Expected counts branch on `FixtureType` and use `ActionCounts` for blobstore/high-level/low-level effects.

## Control flow
Each test prepares source and destination directory state, then calls `rename(old_parent, old_name, new_parent, new_name)`. Same-directory cases rename within `None` or within one nested handle. Cross-directory cases pass distinct source and destination handles. Existing-target setup creates both source and target names before renaming source onto target. Directory and symlink cases verify metadata-object renames, not just regular files.

## State and persistence behavior
Rename mutates directory entries and sometimes removes/replaces target blobs. Same-directory renames generally load one directory blob and write/resize it once. Cross-directory moves update both source and destination directories and may update parent timestamps or backing blocks, producing multiple writes/stores. Replacing an existing target expects `store_remove_by_id`, high-level removals, and low-level removes. Directory and symlink renames look similar to simple file renames because the directory entry changes while object payloads remain intact.

## Dependencies and integration points
The suite depends on directory entry encoding, parent-handle lookup behavior, replacement semantics, and fixture-driver cache behavior. It integrates with `perf_test_macro` but has special macro handling for two cases due to a known deadlock with all fixtures. The exact counts expose differences between fuser with inode cache, fuser without inode cache, and fuse-mt.

## Risks and observations
The file contains many TODOs questioning counts. Fuse-mt often performs fewer writes/stores than fuser in cross-directory moves. Fuser without inode cache frequently performs more loads/read-all operations due to repeated lookups. `to_existing_target` currently expects success and contains a TODO asking whether it should fail instead, making it a semantic risk as well as a performance test. The two fuse-mt-only cases indicate unresolved fixture-level deadlock risk.

## Test signals
The suite validates simple rename cost, cross-directory update cost, deep path lookup scaling, replacement cleanup/removal behavior, and support for directory and symlink renames. It also marks current benchmark/test instability: some scenarios cannot safely run across all fixture types.
