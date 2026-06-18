# sources/storage-engines/tikv/components/collections/src/lib.rs

## Purpose
Exports TiKV-standard hash map and hash set aliases backed by `fxhash::FxHasher`, plus a convenience constructor for pre-sized hash sets.

## APIs and control flow
`HashMap<K,V>` aliases `std::collections::HashMap<K,V,BuildHasherDefault<fxhash::FxHasher>>`. `HashSet<T>` aliases the matching standard set. `HashMapEntry` re-exports `std::collections::hash_map::Entry`. `hash_set_with_capacity` creates a `HashSet` with requested capacity and `FxBuildHasher::default()`.

## State, dependencies, and integration
The module has no global state. It imports `tikv_alloc` for workspace allocation integration and depends on `fxhash`. It is designed as an API convenience crate: downstream modules can choose the TiKV fast-hash defaults without repeating verbose hasher types.

## Risks and test signals
Fast non-cryptographic hashing can be a poor fit for untrusted inputs. Type aliases hide the hasher choice, so changing this file would affect performance and determinism across all users. No local tests exist; compile-time usage by dependents is the main signal.
