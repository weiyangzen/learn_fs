# sources/security-integrity/cryfs/crates/utils/src/async_drop/hash_map.rs

Purpose: `HashMap` container for async-droppable values that cleans all entries concurrently on drop.

Important APIs/types/functions: `AsyncDropHashMap<K,V>` wraps `HashMap<K, AsyncDropGuard<V>>`; exposes `new`, `try_insert`, `remove`, `get`, `get_mut`, `len`, and feature-gated `drain`/`iter`.

Control flow: insertion uses `HashMapExt::try_insert` and rejects duplicate keys with the rejected guard returned in `OccupiedError`. `async_drop_impl` drains values and runs `for_each_unordered` to drop them concurrently.

State/persistence: in-memory map only. Removed/drained values become caller responsibility.

Dependencies/integration: depends on `anyhow`, `HashMapExt`, `OccupiedError`, and `crate::stream::for_each_unordered`.

Risks: duplicate insertion requires the caller to async-drop the rejected value. Concurrent dropping returns the first encountered error depending on stream behavior.

Test signals: unit tests cover empty map, insert/get, duplicate rejection, remove, drop-all, and mutation.
