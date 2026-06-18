<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/option.rs -->
# sources/object-store/garage/src/util/crdt/option.rs

## Purpose
Optional-value CRDT wrappers with two different merge policies: one that cancels on conflict and one that recursively merges present values.

## Important APIs, types, and functions
`CancelingOption<T>(Option<T>)` and `MergingOption<T>(Option<T>)` expose `inner`, `into_inner`, `map`, `From<Option<T>>`, and `Crdt::merge` implementations.

## Control flow
`CancelingOption` keeps a value only if both sides are equal or one side is `None`; conflicting `Some` values collapse to `None`. `MergingOption` treats `None` as absence and recursively merges when both sides are `Some`.

## State and persistence behavior
Both wrappers serialize the optional value as part of metadata. `None` can mean disabled, unset, or conflict depending on the wrapper, so callers must choose policy carefully.

## Dependencies and integration points
Used for optional fields in Garage CRDT metadata, often with nested `Lww` or map values. Depends on base `Crdt` and serde.

## Risks and test signals
The two option types have very different semantics; mixing them can silently change conflict resolution. Tests should cover `Some/None`, equal `Some`, conflicting `Some`, and recursive merge cases.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/crdt/option.rs -->
