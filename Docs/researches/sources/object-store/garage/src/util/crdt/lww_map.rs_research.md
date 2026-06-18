<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/lww_map.rs -->
# sources/object-store/garage/src/util/crdt/lww_map.rs

## Purpose
Sorted map CRDT whose entries are individually last-writer-wins, enabling efficient per-key updates and convergence for metadata dictionaries.

## Important APIs, types, and functions
`LwwMap<K, V>` stores sorted `(K, timestamp, V)` items. Main methods are `new`, `raw_item`, `update_mutator`, `update_in_place`, `merge_raw`, `take_and_clear`, `clear`, `retain`, `get`, `get_timestamp`, `items`, `len`, `is_empty`, `Default`, `Crdt::merge`, and optional `Arbitrary`.

## Control flow
Updates compute a timestamp greater than the current entry timestamp, then `merge_raw` binary-searches by key. Existing entries are replaced only if the incoming timestamp is newer or if timestamp ties and incoming value orders greater. Merge iterates remote items through `merge_raw`.

## State and persistence behavior
The vector is kept sorted for deterministic serialization and binary search. Clearing drops local items but is not itself a replicated tombstone; deletions must be modeled in `V` if they need to propagate.

## Dependencies and integration points
Used in Garage CRDT metadata maps. Depends on ordering for keys and values, logical clock helpers, serde, and `Crdt`.

## Risks and test signals
A plain `clear` is local mutation, not a distributed delete. Value ordering participates in timestamp ties, so `V` ordering must be stable. Tests should check sorted insertion, timestamp tie behavior, retained item filtering, and merge idempotence.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/lww_map.rs -->
