## sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/RangeMap.h

Purpose: Implements a templated interval map over ordered keys using boundary entries, with optional metric aggregation through Flow's indexed map.

Important APIs/types/functions: `RangeMapRange<Key>` and `rangeMapRange()` represent half-open ranges. Metric functors compute constant/key/value/key-value byte metrics. `RangeMap<Key, Val, Range, Metric, MetricFunc>` exposes iterators whose `begin()`, `end()`, `range()`, and `value()` represent logical intervals, plus `ranges()`, `intersectingRanges()`, `containedRanges()`, `rangeContaining()`, `insert()`, `coalesce()`, `allEqual()`, metric sum helpers, and random/nth range selection.

Control flow: The constructor installs a beginning boundary at default `Key()` and an end sentinel at `endKey`. `insert()` ensures an end boundary carrying the prior value, erases overwritten boundaries, inserts a new begin boundary, and leaves coalescing to callers. Iteration stops before the sentinel. `coalesce()` removes adjacent boundaries with equal values around a key or range.

State and persistence behavior: State is an in-memory `Map<Key, Val, pair_type, Metric>` of boundaries and values. `clearAsync()` delegates to the underlying map. No built-in serialization is provided.

Dependencies and integration points: Depends on Flow `MapPair`, `IndexedSet` map implementation, deterministic random, boost iterator ranges, and key/value types with ordering and equality. Used by higher layers needing compact range ownership/state maps.

Risks: Correctness depends on the sentinel invariant: one extra end boundary always exists. Callers must coalesce when they require no adjacent equal ranges. `rangeContainingKeyBefore()` assumes key-like types with `.size()`, so it is oriented toward string/key ranges. Metric functors assume `key` and `value` have `size()` where used.

Test signals: Boundary insertions at beginning/end, overlapping inserts, empty-range no-op, coalescing, sentinel preservation, iterator decrement before begin/end behavior, random/nth range, and metric sums across inserted ranges.
