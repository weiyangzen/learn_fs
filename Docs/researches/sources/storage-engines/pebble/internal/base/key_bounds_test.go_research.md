# sources/storage-engines/pebble/internal/base/key_bounds_test.go

Purpose: Tests user-key boundary and range behavior.

APIs and types: Exercises `UserKeyBoundary.IsUpperBoundFor`, `CompareUpperBounds`, `UserKeyBounds.Valid`, `Overlaps`, `ContainsBounds`, `ContainsUserKey`, `ContainsInternalKey`, `Clone`, `String`, and `Union`.

Control flow and state: Table-driven cases compare inclusive and exclusive ends, unset bounds, adjacent spans, contained spans, and internal keys including sentinel-like boundaries.

Persistence and dependencies: No persistence. Uses the default comparer and require/assert helpers.

Integration points: Protects key span logic consumed by manifest, compaction, and object storage decisions.

Risks: Focused on representative cases; comparator-specific unusual orderings are only indirectly covered by using injected compare functions elsewhere.

Test signals: Strong local coverage for interval semantics.
