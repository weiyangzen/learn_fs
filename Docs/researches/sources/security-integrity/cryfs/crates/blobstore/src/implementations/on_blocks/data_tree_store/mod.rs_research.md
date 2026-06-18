# sources/security-integrity/cryfs/crates/blobstore/src/implementations/on_blocks/data_tree_store/mod.rs

Purpose: module facade for the data-tree layer built on `DataNodeStore`. It groups size caching, store-level APIs, traversal algorithms, and the `DataTree` object, then exports the public surface.

Important APIs and types: declares private modules `size_cache`, `store`, `traversal`, and `tree`, plus test-only `testutils`. Public re-exports are `DataTreeStore`, `LoadNodeError`, and `DataTree`.

Control flow: there is no runtime logic in this file. Compile-time organization ensures external users import the tree store and tree type from this module while implementation details remain private, except `LoadNodeError` which is exposed for subtree streaming failures.

State and persistence behavior: none directly. Persistence is delegated to `store.rs` and `tree/mod.rs`, and size/traversal state is encapsulated in private modules.

Dependencies and integration points: parent modules can depend on `data_tree_store::DataTreeStore` and `DataTree` without knowing file layout. Test utilities are available only under `#[cfg(test)]`, while production exports stay narrow.

Risks: the module boundary hides `size_cache` and traversal internals, so external tests must exercise them through `DataTree` and `DataTreeStore`. That is generally good encapsulation but leaves `SizeCache` with a TODO for direct tests in its own file.

Test signals: indirect; it includes test utilities only for unit tests and exposes the modules whose embedded tests cover behavior.
