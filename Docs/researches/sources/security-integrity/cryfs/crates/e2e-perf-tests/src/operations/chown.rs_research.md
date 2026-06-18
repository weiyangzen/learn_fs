# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/chown.rs

## Purpose
This module defines the `chown` performance counter suite. It measures ownership-change behavior for files, directories, symlinks, and files under increasingly deep parent directories. The operation under test is `fixture.filesystem.chown(Some(node), Some(Uid::from(1000)), Some(Gid::from(1000)))`.

## Important APIs, Types, And Functions
The module registers five cases with `crate::perf_test_macro::perf_test!(chown, [...])`: `file_in_rootdir`, `dir_in_rootdir`, `symlink_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir`. Each case accepts `impl TestDriver` and returns `impl TestReady`, chaining `create_filesystem()`, `setup`, `test`, and `expect_op_counts`.

It depends on `FilesystemDriver` for async filesystem calls, `ActionCounts` for expected aggregate counters, `FixtureType` for backend-specific expectations, and `Uid`/`Gid` from `cryfs_rustfs`. `PathComponent` and `AbsolutePath` build test names and symlink/deep-directory paths.

## Control Flow
Each case creates a fresh filesystem fixture, creates the target object during setup, runs exactly one `chown` in the measured phase, and asserts expected blobstore, high-level blockstore, and low-level blockstore actions. Root file, directory, and symlink cases differ only in setup object type. Nested and deeply nested cases first create parent directories with `mkdir` or `mkdir_recursive`, then create a child file and chown that returned node.

## State And Persistence Behavior
`chown` mutates metadata for an existing node. Expected counters consistently include one blob write and resize plus one low-level store, indicating persisted metadata update. Directory and symlink targets require full blob reads because their metadata/content layout differs from simple cached root files. Deeper paths increase loads and reads for `Fusemt` and especially `FuserWithoutInodeCache`, reflecting path lookup and inode-cache effects.

## Dependencies And Integration Points
The suite is generated across fixture drivers and atime modes by `perf_test!`. It integrates with `FilesystemFixture` through `fixture.filesystem` and with blockstore instrumentation through `BlobStoreActionCounts`, `HLActionCounts`, and `LLActionCounts`. It is sensitive to fixture backend semantics: `FuserWithInodeCache`, `Fusemt`, and `FuserWithoutInodeCache` have separate expected count branches.

## Risks And Edge Cases
Many expected counts are marked with TODO comments questioning correctness, especially why no-cache fuser performs more work than fuse-mt. The tests only cover setting both uid and gid to concrete values; they do not cover uid-only, gid-only, clearing values, permission failures, missing nodes, or chown on root. Since all calls unwrap, any behavior change fails hard but does not classify errors.

## Test Signals
Strong signals are fixed expected `store_load`, `blob_read_all`, `blob_read`, `blob_write`, `blob_resize`, `blob_num_bytes`, `blob_data`, `blob_data_mut`, `load`, and `store` counts per fixture type. Regressions in metadata persistence, path traversal cost, or inode-cache behavior should appear as counter mismatches.
