# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/rmdir.rs

## Purpose
This file defines e2e performance counter scenarios for the filesystem `rmdir` operation. It is not the implementation of directory removal; it is a fixture-driven specification of expected blobstore, high-level blockstore, and low-level blockstore activity for removing directories across root, nested, deeply nested, invalid-target, and large-directory cases.

## Important APIs, Types, and Functions
The file registers the `rmdir` test group with `crate::perf_test_macro::perf_test!`, listing sixteen scenario functions. Each scenario accepts `impl TestDriver` and returns `impl TestReady` through the builder chain `create_filesystem().setup(...).test(...).expect_op_counts(...)`.

The scenario set covers `existing_empty_dir_from_rootdir`, missing directory lookup, non-empty directory failure, empty/non-empty/missing children under nested and deeply nested parents, attempts to remove files or symlinks via `rmdir`, and `rmdir_large_directory`. It uses `PathComponent::try_from_str` for child names, `AbsolutePath::try_from_str` for recursive setup paths, and `NUM_BYTES_FOR_THREE_LEVEL_TREE / BLOCKID_LEN` to size the large directory stress case.

## Control Flow
Every scenario creates a fresh filesystem, performs setup that is later excluded from counted operations by the test driver, then runs one counted `fixture.filesystem.rmdir(parent, name)` call or a loop of calls. Successful paths unwrap the result. Error cases use `unwrap_err()` to assert expected failure while still checking the storage actions needed to detect that failure.

The large-directory test first creates a directory and enough subdirectories to force multi-level directory storage. The counted phase removes every subdirectory, then removes the parent directory after it becomes empty.

## State and Persistence Behavior
The scenarios mutate directory metadata and backing blobs through the filesystem abstraction. Successful removals shrink or rewrite parent directory blobs, remove child directory blobs, and flush dirty blocks. Failure cases usually still load and inspect parent or child metadata; several nested failure cases also count parent directory rewrite/resize behavior, reflecting lookup or atime/cache side effects.

## Dependencies and Integration Points
The tests depend on `FilesystemDriver`, `TestDriver`, `TestReady`, `ActionCounts`, `BlobStoreActionCounts`, `HLActionCounts`, `LLActionCounts`, `FixtureType`, `BLOCKID_LEN`, and CryFS path types. They integrate with the generated test matrix from `perf_test_macro.rs`, which runs them against fuser with inode cache, fuser without inode cache, fuse-mt, and multiple atime modes.

## Risks and Notes
Many expected counts carry TODO comments asking whether they are really expected. Several fixture-specific branches document that fuser without inode cache performs more loads than fuse-mt, likely because node handles store paths and force repeated lookup. These numbers are therefore regression-sensitive but may also encode current implementation artifacts. Large-directory constants are tightly coupled to block tree fanout and `BLOCKID_LEN`.

## Test Signals
The strongest signals are exact equality of counted `ActionCounts` and distinct expected values per `FixtureType`. The suite exercises success, ENOENT-like failure, ENOTEMPTY-like failure, type mismatch errors for file/symlink targets, path depth overhead, and block-tree removal costs.
