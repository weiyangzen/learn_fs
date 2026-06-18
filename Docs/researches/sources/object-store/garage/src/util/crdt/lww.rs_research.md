<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/lww.rs -->
# sources/object-store/garage/src/util/crdt/lww.rs

## Purpose
Last-writer-wins CRDT wrapper around a value with a logical timestamp, used for mutable metadata fields where the newest update should dominate.

## Important APIs, types, and functions
`Lww<T>` stores `timestamp` and `value`. It exposes `new`, `raw`, `update`, `timestamp`, `get`, `take`, `get_mut`, `map`, `Default`, and `Crdt::merge`.

## Control flow
`new` and `update` choose timestamps using Garage logical clock helpers. `merge` replaces local state when the remote timestamp is newer; when timestamps tie, the greater value is kept to make convergence deterministic.

## State and persistence behavior
Timestamp and value are serialized with table entries. The logical clock ties wall time to monotonic increments, helping updates survive skew and repeated local writes.

## Dependencies and integration points
Depends on `time::increment_logical_clock`, serde, and `Crdt`. Frequently nested in bucket/key/user metadata CRDTs and maps.

## Risks and test signals
Clock skew and equal timestamp tie-breaking can surprise callers if values are not naturally ordered. `get_mut` can mutate without timestamp update, so it should be used carefully. Tests should cover newer timestamp dominance, tie ordering, update monotonicity, and default behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/lww.rs -->
