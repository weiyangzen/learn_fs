<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/inmemory.rs -->
# sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/inmemory.rs

## Purpose
Implements a simple in-memory low-level blockstore backed by an `RwLock<HashMap<BlockId, Data>>`.

## APIs, Flow, And State
`InMemoryBlockStore::new` returns an async-drop guard. Reader methods lock the map for `exists`, `load`, `num_blocks`, and `all_blocks`; load clones stored `Data`, and all-blocks snapshots keys into a vector-backed stream. Free-space estimate uses `sysinfo` available memory, and overhead is zero. Writer methods implement optimized allocation with a local `BlockData` wrapper, `try_create_optimized`, and `store_optimized`. Remove deletes from the map and returns `RemoveResult`.

## Dependencies And Integration
Implements `BlockStoreReader`, `BlockStoreDeleter`, `OptimizedBlockStoreWriter`, `AsyncDrop`, and `LLBlockStore`. Used heavily by tests as the base low-level store under locking, encryption, compression, and blobstore implementations.

## Risks And Test Signals
State is process-local and non-persistent; it is appropriate for tests and transient stores. Poisoned lock acquisition is converted into `anyhow` errors. Tests run the generic low-level suite and verify zero-overhead size conversions.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/blockstore/src/low_level/implementations/inmemory.rs -->
