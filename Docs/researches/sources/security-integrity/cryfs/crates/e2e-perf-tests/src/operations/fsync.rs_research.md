# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/fsync.rs

## Purpose
This module defines the largest fsync-related performance suites. It registers both `fsync_datasync` and `fsync_fullsync`, measuring `filesystem.fsync(file, &mut fh, DATASYNC)` across clean files, dirty small writes, dirty large writes, in-place writes, beyond-end writes, path depths, and optional release after sync.

## Important APIs, Types, And Functions
Two `perf_test!` invocations instantiate the same scenario list with `DATASYNC=true` and `DATASYNC=false`. Every scenario is also instantiated with `CLOSE_AFTER=false` and `true`. Important functions include `unchanged_empty_file_in_rootdir`, `unchanged_file_with_data_in_rootdir`, `unchanged_large_file_in_rootdir`, `unchanged_file_in_nested_dir`, `unchanged_file_in_deeply_nested_dir`, `after_small_write_to_empty_file`, `after_small_write_to_middle_of_small_file`, `after_small_write_beyond_end_of_small_file`, `after_small_write_to_middle_of_large_file`, `after_small_write_beyond_end_of_large_file`, `after_large_write_to_empty_file`, `after_large_write_to_middle_of_large_file`, `after_large_write_beyond_end_of_large_file`, `after_write_to_file_in_nested_dir`, and `after_write_to_file_in_deeply_nested_dir`.

The module uses `test_noflush` and `setup_noflush` to preserve dirty state until the measured `fsync`, `NumBytes` for offsets and sizes, `BLOCKSIZE_BYTES`, `NUM_BYTES_FOR_THREE_LEVEL_TREE`, and `maybe_close`.

## Control Flow
Clean-file scenarios create/open a file and sometimes pre-write data in setup, then run `fsync` without an automatic fixture flush. Dirty scenarios create/open a file, use `setup_noflush` to perform a write that remains unflushed, then measure `fsync`. The write matrix covers one-byte writes, block-middle writes, writes beyond EOF, large writes of `NUM_BYTES_FOR_THREE_LEVEL_TREE`, and nested/deep parent paths. After `fsync`, the test may release the handle.

Expected counters derive both `datasync` and `close_after` as integers. Many expressions subtract metadata writes when datasync is true and the handle is not closed, while close-after adds release flush work.

## State And Persistence Behavior
`fsync` persists dirty file data and sometimes metadata, with datasync expected to avoid some metadata persistence when the handle remains open. Clean files mostly flush already-open stores and show load/read/flush counters without resize/write. Dirty writes introduce `blob_resize`, `blob_write`, `blob_data_mut`, low-level `store`, and high-level `store_flush_block`. Large file scenarios load and flush more high-level blocks. Nested and deep cases add path traversal overhead, especially for no-cache fuser.

The explicit TODO block at the top flags uncertainty around flush operations loading low-level blocks and some flush-after-write paths not storing low-level data.

## Dependencies And Integration Points
This suite is tightly coupled to the filesystem fixture's no-flush phases and to the blockstore instrumentation model. It exercises `FilesystemDriver::write`, `fsync`, `release`, `mkdir`, `mkdir_recursive`, and `create_and_open_file`. It is generated across all fixture types and atime behaviors, making it a broad integration signal for fuser, fuse-mt, cache, and persistence layers.

## Risks And Edge Cases
The module contains many empirical counter formulas, making it sensitive to legitimate storage-layout or cache changes. It does not assert file contents after sync, crash recovery, or exact datasync/fullsync durability semantics outside counters. It covers files only, not directory fsync. The arithmetic formulas can obscure intended behavior and are vulnerable to off-by-one mistakes when close and datasync interact.

## Test Signals
Primary signals are differences between datasync and fullsync, clean and dirty files, small and large file trees, in-place and beyond-EOF writes, and close/no-close release behavior. Counter mismatches in `blob_flush`, `blob_resize`, `blob_write`, `store_flush_block`, `blob_data_mut`, low-level `store`, and load counts point to persistence or cache behavior changes.
