<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/deletable.rs -->
# sources/object-store/garage/src/util/crdt/deletable.rs

## Purpose
CRDT wrapper representing either a present value or a deletion tombstone, allowing deletions to dominate stale present values during merge.

## Important APIs, types, and functions
`Deletable<T>` has `Present(T)` and `Deleted` variants. Helpers include `map`, `present`, `delete`, option conversion methods, `is_deleted`, `From<Option<T>>`, `From<Deletable<T>> for Option<T>`, and `Crdt::merge`.

## Control flow
A present value merged with another present value recursively merges the inner CRDT. Any merge involving `Deleted` results in `Deleted`, making deletion absorbing.

## State and persistence behavior
The tombstone must be persisted long enough for anti-entropy to suppress stale live values. It does not carry deletion time by itself; callers combine it with LWW wrappers when ordering matters.

## Dependencies and integration points
Used by metadata structures with delete semantics and table filters such as `DeletedFilter`. Depends on the base `Crdt` trait and serde derives.

## Risks and test signals
Because deletion is permanent inside this wrapper, recreating an entity generally needs a fresh outer timestamp/key generation strategy. Tests should verify tombstone dominance and recursive merge for present values.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/deletable.rs -->
