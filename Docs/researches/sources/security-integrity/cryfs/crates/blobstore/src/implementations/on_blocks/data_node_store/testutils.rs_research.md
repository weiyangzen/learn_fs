# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/testutils.rs

Purpose: supplies deterministic constructors and assertions for `DataNodeStore` unit tests. It standardizes physical block size, random data generation, node creation, typed loading, and validation helpers.

Important APIs and types: `PHYSICAL_BLOCK_SIZE` is 1024 bytes. Helpers include `new_full_leaf_node`, `new_empty_leaf_node`, `new_inner_node`, `new_full_inner_node`, `new_full_leaves`, `new_inner_nodes`, `load_node`, `load_inner_node`, `load_leaf_node`, `with_nodestore`, `with_nodestore_with_blocksize`, `half_full_leaf_data`, `full_leaf_data`, `data_fixture`, and `assert_full_inner_node_is_valid`.

Control flow: fixture runners create a `DataNodeStore<LockingBlockStore<InMemoryBlockStore>>`, pass a borrowed store into an async closure, then explicitly `async_drop` it. Node factories create leaves and inner nodes through the public store APIs, often using `future::join_all` or `join!` to create multiple children concurrently. Typed load helpers panic on unexpected node kind, which keeps tests concise and fails loudly on serialization or parsing mistakes.

State and persistence behavior: all helpers use in-memory stores, but they still go through `DataNodeStore` serialization and lower-store APIs. Deterministic data comes from `SmallRng::seed_from_u64`, making expected payloads reproducible. Full/half leaf helpers derive sizes from `NodeLayout`, so tests track header-size changes.

Dependencies and integration points: used by `data_node_store/mod.rs` tests and indirectly by tree test helpers. Depends on `rand`, `futures`, `byte_unit`, local `NodeLayout`, and the in-memory locking block store. It intentionally uses public APIs rather than constructing raw nodes directly, so helper failures reveal public contract regressions.

Risks: panics and unwraps are acceptable in tests but can obscure underlying errors if a helper is reused in broader harnesses. `new_inner_node` creates a depth-1 inner node with two leaves; it does not validate deeper structure. The commented shared-block helper suggests historical/shared-cache test setups were removed or deferred.

Test signals: the helper set enables coverage of empty, half-full, full, and multi-child nodes; deterministic data comparison; and validation that inner nodes have expected depth, child count, and loadable children.
