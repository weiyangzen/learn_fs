# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/truncate.rs

## Purpose
This file defines performance counter scenarios for path/node based `truncate`. It measures growing and shrinking empty or non-empty files, truncating files in root/nested/deeply nested locations, and expected failures when the target is a directory or symlink.

## Important APIs, Types, and Functions
The `truncate` group lists eleven scenario functions. The counted operation is `fixture.filesystem.truncate(Some(node), NumBytes::from(size))`. Sizes include one byte, 100/101 bytes, 1024 bytes, and `NUM_BYTES_FOR_THREE_LEVEL_TREE` to force multi-level block-tree allocation or removal.

The scenarios use `create_file`, `mkdir`, `mkdir_recursive`, and `create_symlink` during setup. Counts are fixture-specific for lookup depth and cache behavior, using `FixtureType` matches in expected `ActionCounts`.

## Control Flow
Each scenario creates a fresh filesystem and target node. Grow tests truncate an empty or short file upward. Shrink tests first grow a file to the large tree size in setup, then shrink during the counted phase. Location tests create files under root, one nested directory, or a recursive deep path. Error tests create a directory or symlink and assert `expect_err` from `truncate`.

## State and Persistence Behavior
Growing a file resizes file data and may allocate high-level blocks and low-level blocks. Large grows record `store_create` and low-level `exists`/`store` counts. Shrinking a large file removes block tree nodes, including `store_remove` and `store_remove_by_id` counts. Failed directory or symlink truncation should inspect metadata and return without data-block mutation.

## Dependencies and Integration Points
The file depends on `FilesystemDriver`, the test-driver builder, `ActionCounts`, `FixtureType`, `NumBytes`, path types, and the block-size stress constant. It is generated into a broad fixture/atime matrix by `perf_test_macro.rs`.

## Risks and Notes
Expected counts are implementation-coupled, especially around cached node handles and whether metadata loads include `blob_read_all` or `blob_num_bytes`. Large truncate tests encode current block-tree shape; changes to tree layout, allocation granularity, or sparse-file semantics will require count updates.

## Test Signals
The tests cover small versus large growth, small versus large shrink, root/nested/deep lookup overhead, type validation errors, allocation counts, removal counts, and exact low-level blockstore effects for multi-level file data changes.
