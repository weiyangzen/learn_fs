<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/tree/tests_performance.rs -->
# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/tree/tests_performance.rs

## Purpose
Defines performance-oriented async tests for the on-blocks `DataTree` implementation. These tests do not measure elapsed time; they assert exact low-level blockstore action counts so tree operations only load, check, or store the structurally necessary nodes.

## APIs, Flow, And State
The file fixes a small `NodeLayout` with 40-byte blocks, `NUM_LEAVES = 100`, and derived `DEPTH`, `NUM_NODES`, and `NUM_BYTES`. `testutils` builds a `DataTreeStore<LockingBlockStore<LLSharedBlockStore<LLTrackingBlockStore<InMemoryBlockStore>>>>`, creates empty/nonempty trees, flushes caches, resets counters, and computes expected tree-node counts with `divrem::DivCeil`. Tests cover `num_nodes`, `num_bytes`, `create_tree`, `try_create_tree`, read variants through `instantiate_read_tests!`, `read_all`, and many `write_bytes` cases.

Control flow repeatedly creates or loads a tree, optionally warms the size cache with `num_bytes`, prunes unloaded cache entries, runs one tree operation, then compares `LLActionCounts` against expected loads/stores/exists calls. Write tests also drop the tree and clear the cache to force dirty node flushes before asserting store counts. State under test is the in-memory blockstore plus the locking block cache and the tree's internal node/size caches.

## Dependencies And Integration
Integrates `DataTreeStore` and `DataTree` with the high-level locking blockstore and low-level tracking/shared/in-memory wrappers from `cryfs_blockstore`. It relies on `pretty_assertions`, Tokio multi-thread tests, `BoxFuture`, and helper functions from the surrounding tree test utilities such as `expected_depth_for_num_leaves`.

## Risks And Test Signals
The file is a strong regression signal for accidental O(tree) or O(file) behavior in tree reads/writes. Several assertions intentionally encode known inefficiencies with TODOs: reads without size cache use hard-coded extra loads, full-leaf writes unexpectedly perform `exists`, and growing writes include unexplained fixed offsets like `+3` stores. Missing areas are called out at the end: `resize_num_bytes`, `remove`, and `all_blocks` performance are not covered here.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/tree/tests_performance.rs -->
