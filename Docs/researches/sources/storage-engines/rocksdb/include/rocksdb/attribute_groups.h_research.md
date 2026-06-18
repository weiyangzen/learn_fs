# sources/storage-engines/rocksdb/include/rocksdb/attribute_groups.h

## Purpose
`attribute_groups.h` defines the public types used to group wide-column attributes across RocksDB column families. The write path uses owning `AttributeGroup` values, the read path uses pinnable `PinnableAttributeGroup` values, and iterator paths use pointer-backed `IteratorAttributeGroup` values to avoid copying wide-column collections while scanning. The file also defines the abstract `AttributeGroupIterator` interface for cross-column-family iteration.

## Important APIs, Types, And Functions
`AttributeGroup` owns a `ColumnFamilyHandle*` and a `WideColumns` collection. It exposes `column_family()`, const and mutable `columns()`, and equality/inequality operators that compare the column-family handle pointer and column contents. `AttributeGroups` is a `std::vector<AttributeGroup>`, with `kNoAttributeGroups` declared as the external empty constant.

`PinnableAttributeGroup` stores a `ColumnFamilyHandle*`, a `Status`, and `PinnableWideColumns`. It exposes accessors for the column family, status, and `WideColumns` view, plus `SetStatus`, `SetColumns(PinnableWideColumns&&)`, and `Reset()`. `Reset()` returns status to `Status::OK()` and resets the pinnable columns. `PinnableAttributeGroups` is a `std::vector<PinnableAttributeGroup>`.

`IteratorAttributeGroup` stores a `ColumnFamilyHandle*` and a `const WideColumns*`. It can be built directly from a handle and pointer, or from an `AttributeGroup`, in which case it points at the original group's columns. Its equality operators compare the handle pointer and dereferenced column contents. `IteratorAttributeGroups` is a `std::vector<IteratorAttributeGroup>`, with `kNoIteratorAttributeGroups` declared externally.

`AttributeGroupIterator` derives from `IteratorBase`, disables copying, has a virtual destructor, and adds one pure virtual method: `const IteratorAttributeGroups& attribute_groups() const`.

## Control Flow
The file is mostly type declarations with inline accessors. Write callers construct `AttributeGroup` objects with a target column-family handle and owned wide columns, then pass vectors through APIs that understand wide-column entities. Read callers construct or receive `PinnableAttributeGroup` objects, fill each group with either a status or moved pinnable columns, and call `Reset()` before reuse.

Iterator control flow is pointer-oriented. `IteratorAttributeGroup` avoids copying `WideColumns` during iteration by retaining a pointer to columns owned elsewhere, usually an `AttributeGroup` or iterator-internal storage. `AttributeGroupIterator::attribute_groups()` returns the current key's grouped columns in comparator order across column families.

## State And Persistence Behavior
These types do not persist data by themselves. They are transient API containers around column-family handles and wide-column data. `AttributeGroup` owns its `WideColumns`; `PinnableAttributeGroup` owns a `PinnableWideColumns` wrapper whose underlying buffers may be pinned to RocksDB-managed memory; `IteratorAttributeGroup` is non-owning and depends on the lifetime of the pointed-to `WideColumns`.

The `ColumnFamilyHandle*` fields are raw pointers and are compared by identity. The file does not manage handle lifetimes, reference counts, or column-family persistence. Any durable behavior comes from the DB write/read/iterator operations that consume or produce these groups.

## Dependencies And Integration Points
The header includes `rocksdb/iterator_base.h` and `rocksdb/wide_columns.h`, and forward-declares `ColumnFamilyHandle`. It depends on `Status`, `WideColumns`, `PinnableWideColumns`, and `IteratorBase` from RocksDB public APIs.

Integration points are wide-column write APIs, entity reads, multi-column-family reads, and cross-column-family iterators. `AttributeGroupIterator` follows the same basic iterator lifecycle as other `IteratorBase` derivatives while exposing grouped wide columns instead of a single value.

## Risks
The main risk is lifetime safety. `IteratorAttributeGroup` dereferences a raw `const WideColumns*`, so producers must ensure the referenced columns outlive the returned iterator groups and remain stable until the next iterator movement or invalidation point. Similarly, `PinnableAttributeGroup::columns()` exposes data whose backing may be pinned and reset, so callers must not retain references after `Reset()` or object reuse.

Handle identity comparisons can surprise code expecting logical column-family equality. Two handles for the same column family would compare unequal if their pointers differ, while a stale/destroyed handle pointer would be unsafe. The header does not guard against null handles or null column pointers.

Because `AttributeGroupIterator` is abstract, implementations must maintain the base iterator status/validity/key ordering contracts in addition to returning attribute groups in comparator order. Returning references to temporary vectors or columns would be a correctness bug.

## Test Signals
Tests should cover equality/inequality for owned and iterator groups, mutation through non-const `AttributeGroup::columns()`, `PinnableAttributeGroup` status/column setting and reset behavior, and empty constants. Iterator tests should verify stable group contents at valid positions, invalidation after movement/reset/destruction, correct cross-column-family ordering, and behavior when a per-group read status is non-OK.
