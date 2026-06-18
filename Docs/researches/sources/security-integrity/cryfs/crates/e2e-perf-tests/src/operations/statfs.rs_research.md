# sources/security-integrity/cryfs/crates/e2e-perf-tests/src/operations/statfs.rs

## Purpose
This file defines performance counter tests for `statfs`, validating that filesystem statistics queries use only storage-level capacity and block-count APIs and do not scale with existing directory or file content.

## Important APIs, Types, and Functions
The group is registered as `perf_test!(statfs, [empty_filesystem, with_content])`. `empty_filesystem` calls `fixture.filesystem.statfs()` on a fresh filesystem. `with_content` creates a directory, a root file, and a nested file before the counted `statfs` call.

Expected counts are expressed with `BlobStoreActionCounts`, `HLActionCounts`, and `LLActionCounts`. Both scenarios expect `store_num_nodes`, `store_estimate_space_for_num_blocks_left`, `store_logical_block_size_bytes`, `store_num_blocks`, `store_estimate_num_free_bytes`, `num_blocks`, and `estimate_num_free_bytes` once.

## Control Flow
Each test uses the standard `create_filesystem().setup(...).test(...).expect_op_counts(...)` chain. Setup is either empty or creates representative content. The counted phase only invokes `statfs` and unwraps success.

## State and Persistence Behavior
`statfs` is read-only from the filesystem caller perspective. It should not load file or directory blobs and should not write, resize, remove, or flush data. The identical expected counts for empty and populated filesystems intentionally verify content independence.

## Dependencies and Integration Points
This file uses `FilesystemDriver` as an imported trait, `TestDriver`/`TestReady`, `ActionCounts`, CryFS path components for setup names, and the blobstore/blockstore counter types. It integrates with all fixture and atime combinations produced by the macro, although expected counts do not vary by fixture type or atime behavior.

## Risks and Notes
The main risk is that future `statfs` implementation changes begin walking content or loading metadata, which would invalidate the constant-count assumption. The populated setup is small; it verifies non-empty state but not very large filesystems.

## Test Signals
The tests signal that `statfs` should use aggregate store queries exactly once each and remain free of blob reads and writes regardless of simple filesystem content.
