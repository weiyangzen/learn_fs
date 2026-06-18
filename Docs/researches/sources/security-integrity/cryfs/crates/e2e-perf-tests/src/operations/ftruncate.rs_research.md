# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/ftruncate.rs

## Purpose
This module defines the `ftruncate` performance counter suite for resizing open files. It measures small and large growth, small and large shrink, growth of nonempty files, and ordinary truncate-to-1024 behavior at root, nested, and deeply nested paths. Every scenario is run with and without closing the handle afterward.

## Important APIs, Types, And Functions
The registered functions are `grow_empty_file_small`, `grow_empty_file_large`, `shrink_file_small`, `shrink_file_large`, `grow_nonempty_file_small`, `grow_nonempty_file_large`, `file_in_rootdir`, `file_in_nesteddir`, and `file_in_deeplynesteddir`, all parameterized by `const CLOSE_AFTER: bool`. The operation under test is `filesystem.ftruncate(file.clone(), &file_handle, NumBytes::from(...))`.

The suite uses `NUM_BYTES_FOR_THREE_LEVEL_TREE` to force multi-block tree allocation/removal, `NumBytes` for sizes, `maybe_close` for optional release, and the usual fixture/action-count types.

## Control Flow
Each case creates and opens a file. Growth cases truncate empty or pre-sized files to a larger value. Shrink cases first grow a file to `NUM_BYTES_FOR_THREE_LEVEL_TREE` in setup, then shrink to either one byte less or one byte. Nonempty growth cases pre-truncate to 100 bytes, then grow slightly or to the large tree size. Path-depth cases create parent directories and truncate to 1024 bytes.

Expected counts are computed from `close_after` and fixture type. Large growth expects many high-level `store_create` and low-level `exists`/`store` operations; large shrink expects removal counts.

## State And Persistence Behavior
`ftruncate` changes file size and can allocate or remove block-tree nodes. Small growth/shrink mainly resize metadata/data blobs. Large growth creates many stores and mutates many high-level blob-data entries. Large shrink removes high-level and low-level blocks (`store_remove`, `store_remove_by_id`, `remove`). Optional close adds flush and store work. Path depth mostly changes lookup cost; file tree size changes allocation/removal cost.

## Dependencies And Integration Points
The suite exercises open-file resize semantics in the `FilesystemDriver`, storage tree sizing constants in the fixture, and release behavior through `maybe_close`. It integrates with both fuser and fuse-mt generated tests and all atime behaviors.

## Risks And Edge Cases
There are no tests for truncating directories, invalid handles, permission failures, sparse holes beyond the covered write-free growth, or zero-size shrink from nonempty file except indirectly through small sizes. The large-tree constants tightly couple expected counts to internal tree fanout. TODOs flag uncertainty about no-cache fuser overhead.

## Test Signals
Strong signals are allocation counts for large growth (`store_create`, `exists`, high-level `blob_data_mut`), removal counts for large shrink, and close-driven flush/store counters. The suite should catch changes in file tree representation, sparse resize policy, and release durability.
