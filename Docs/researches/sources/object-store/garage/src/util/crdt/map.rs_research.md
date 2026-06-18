<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/map.rs -->
# sources/object-store/garage/src/util/crdt/map.rs

## Purpose
Sorted map CRDT where values merge recursively instead of being overwritten by timestamps.

## Important APIs, types, and functions
`Map<K, V>` stores sorted `(K, V)` pairs. It provides `new`, `put_mutator`, `put`, `clear`, `get`, `items`, `len`, `is_empty`, `Default`, `FromIterator`, `Crdt::merge`, and optional `Arbitrary`.

## Control flow
`put` binary-searches by key and either replaces the local value or inserts at the sorted position. `merge` iterates remote items, recursively merging values for existing keys and inserting missing keys.

## State and persistence behavior
Deterministic sorted representation is serialized with metadata entries. Like `LwwMap`, `clear` is local and not a replicated deletion unless values encode tombstones.

## Dependencies and integration points
Used for nested metadata maps whose values are CRDTs. Depends on `Ord` keys, `Crdt` values, serde, and optional arbitrary fuzzing.

## Risks and test signals
Replacing a value with `put` can discard local nested CRDT state before merge; callers should use mutator patterns intentionally. Tests should cover sorted order, recursive merge, empty/default, and from-iterator behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/map.rs -->
