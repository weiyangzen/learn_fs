# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/test_as_blockstore/block_store_adapter.rs

Purpose: provides `BlockStoreAdapter`, a test-only wrapper that makes `DataNodeStore<LockingBlockStore<InMemoryBlockStore>>` satisfy the low-level block-store test traits. It lets the standard `cryfs_blockstore` low-level suite validate data-node leaf storage as if it were a block store.

Important APIs and types: `MAX_BLOCK_SIZE` gives the adapter a large physical block size; `BlockStoreAdapter(AsyncDropGuard<DataNodeStore<...>>)` owns the node store; `new` builds an in-memory locking lower store; `clear_cache_slow` supports flush-sensitive fixtures; `load_leaf` loads and rejects inner nodes. Trait implementations cover `BlockStoreReader`, `BlockStoreDeleter`, `BlockStoreWriter`, `Debug`, `AsyncDrop`, `LLBlockStore`, and `LLFixture` through `TestFixtureAdapter<const FLUSH_CACHE_ON_YIELD: bool>`.

Control flow: reads call `load_leaf` and convert leaf payloads back to `Data`; `exists` is a load check; `num_blocks` delegates to `num_nodes`; `all_blocks` delegates to test-only `all_nodes`. Deletion loads the leaf first, then removes its upcast node or reports `NotRemovedBecauseItDoesntExist`. `try_create` performs an existence check before `store`; `store` calls `overwrite_with_leaf_node`, which means a specific ID is written by overwriting that ID as a leaf rather than using random ID allocation.

State and persistence behavior: all storage is in memory under the wrapped `DataNodeStore`; optional fixture yielding can clear the underlying cache to force reload paths. `estimate_num_free_bytes` converts estimated free physical blocks back into logical leaf bytes. The adapter declares overhead equal to the serialized node header offset, matching the leaf payload loss introduced by `DataNodeStore`.

Dependencies and integration points: imports low-level block-store test traits/macros from `cryfs_blockstore::tests::low_level`, the `DataNodeStore` API, local layout constants, and async-drop utilities. It is used by `test_as_blockstore/mod.rs` to instantiate the same block-store conformance suite with and without cache flushing.

Risks: `store` does not check existence and can overwrite existing entries, which is consistent with `BlockStoreWriter::store` but must be distinguished from `try_create`. `load_leaf` panics if an inner node appears, relying on the adapter suite to only create leaves. Capacity and overhead are approximate test translations rather than production allocation logic.

Test signals: the adapter itself is exercised indirectly by the full low-level block-store test suite in two cache modes, giving broad coverage for existence, load, create, overwrite, remove, enumeration, and async drop behavior.
