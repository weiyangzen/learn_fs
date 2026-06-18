# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_node_store/test_as_blockstore/mod.rs

Purpose: wires `BlockStoreAdapter` into the reusable low-level block-store test matrix. This is a compact test module whose role is integration, not production behavior.

Important APIs and types: it declares `mod block_store_adapter;` and two nested test modules, `with_flushing` and `without_flushing`. Each invokes `cryfs_blockstore::instantiate_blockstore_tests_for_lowlevel_blockstore!` with `block_store_adapter::TestFixtureAdapter<true>` or `<false>` and the `"multi_thread"` flavor.

Control flow: when compiled for tests, the macro expands a suite of low-level block-store conformance tests. The `with_flushing` variant clears adapter caches on fixture yield; `without_flushing` leaves caches warm. This makes the same behavioral expectations run over both persisted/reloaded and cache-resident paths.

State and persistence behavior: this file owns no state. Its key persistence signal is that all adapter operations must pass with cache flushing enabled, meaning correctness cannot depend solely on in-memory `DataNode` handles.

Dependencies and integration points: depends on the sibling `block_store_adapter` module and the shared `cryfs_blockstore` test macro. It integrates `DataNodeStore` testing with the lower-level block-store contract, complementing the node-store-specific tests in `data_node_store/mod.rs`.

Risks: because behavior is macro-generated, test coverage is less visible from this file alone. The suite only validates the data-node store when used as leaf-only block storage; it does not validate inner-node tree semantics.

Test signals: strong conformance signal for the leaf-as-block behavior across both flushed and unflushed cache modes, with multi-thread flavor selected.
