# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/testutils.rs

Purpose: provides fixtures and expected-value calculators for `DataTreeStore`/`DataTree` tests, especially multi-leaf and slow feature-gated tree tests.

Important APIs and types: `PHYSICAL_BLOCK_SIZE` is 128 bytes to force shallow tests into multi-node trees. `TreeFixture` records `root_id`, data seed, and byte length, with constructors `create_tree_with_data` and `create_tree_with_data_and_id` plus `assert_data_is_still_intact`. Other helpers create one-leaf/multi-leaf trees, return root IDs, manually build packed trees from leaves upward, run store fixtures with optional shared node-store access, and compute `expected_num_nodes_for_num_leaves`, `expected_depth_for_num_leaves`, and feature-gated `expected_depth_for_num_bytes`.

Control flow: high-level tree constructors use public `DataTreeStore` APIs and resize/write data through `DataTree`. `manually_create_tree` constructs leaves first, then repeatedly groups child IDs into inner nodes until one root remains, mirroring the expected left-packed tree shape. Fixture runners create in-memory locking stores and explicitly async-drop tree and node stores after the closure.

State and persistence behavior: fixtures use deterministic `DataFixture` bytes and in-memory backing stores. The shared-store helper creates both a `DataTreeStore` and a separate `DataNodeStore` over an `LLSharedBlockStore`, allowing tests to inspect raw node counts and tree structure beneath the public tree API. Cache clearing is used in slow tests to force reload/recalculation.

Dependencies and integration points: used by `store.rs` tests and `tree/tests.rs`. Depends on `DataNodeStore`, `DataTreeStore`, `DataTree`, `LLSharedBlockStore`, `LockingBlockStore`, and `iter_chunks` under slow-test features.

Risks: expected-value functions assume the same left-packed invariant as production, so a shared mistaken invariant could hide bugs. Manual tree construction is feature-gated for slow tests and has many unwraps. Very small physical block sizes are useful for coverage but may not mirror production performance characteristics.

Test signals: enables verification of data preservation, raw node counts, depth calculations, root IDs, and exact tree shape across different block sizes and tree sizes.
