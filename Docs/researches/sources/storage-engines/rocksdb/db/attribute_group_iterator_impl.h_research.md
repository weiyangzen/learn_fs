# sources/storage-engines/rocksdb/db/attribute_group_iterator_impl.h

## Purpose
Declares the concrete `AttributeGroupIterator` implementation built on top of `MultiCfIteratorImpl`, plus an error/empty iterator implementation.

## Important APIs and Types
`AttributeGroupIteratorImpl` constructs `impl_` with reset and populate functors bound to `this`. It forwards validity, seeking, movement, key, status, and `PrepareValue` to `MultiCfIteratorImpl`. `attribute_groups()` asserts validity and returns the populated groups. `ResetFunc` clears `attribute_groups_`; `PopulateFunc` delegates to `AddToAttributeGroups`. `EmptyAttributeGroupIterator` always invalidly reports a fixed status, no-ops seeks, asserts on movement/key access, and returns `kNoIteratorAttributeGroups`. `NewAttributeGroupErrorIterator` creates the empty error iterator.

## State, Dependencies, and Risks
State is a `MultiCfIteratorImpl` plus current `IteratorAttributeGroups`. The main risk is reference lifetime for wide-column pointers and assertion-only protection on invalid access. Integration points include multi-CF iteration, wide-column/attribute-group APIs, and callers needing a status-carrying iterator when construction fails.
