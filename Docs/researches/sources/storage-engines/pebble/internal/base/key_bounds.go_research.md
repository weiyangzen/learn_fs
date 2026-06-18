# sources/storage-engines/pebble/internal/base/key_bounds.go

Purpose: Defines user-key ranges and boundaries with inclusive/exclusive endpoint semantics, including conversion from internal key bounds.

APIs and types: `KeyRange`, `BoundaryKind`, `UserKeyBoundary`, `UserKeyBounds`, constructors (`UserKeyInclusive`, `UserKeyExclusive`, `UserKeyBoundsInclusive`, `UserKeyBoundsEndExclusive`, `UserKeyBoundsFromInternal`), and methods for validation, containment, overlap, cloning, formatting, and union.

Control flow and state: Bound comparisons use `Compare` callbacks and special handling for exclusive sentinel internal keys. `UserKeyBounds.Valid` requires non-empty bounds and an end that includes the start. `Union` treats unset bounds as identity and expands start/end as needed.

Persistence and dependencies: No direct persistence, but these structures describe persisted object key spans for tables and blobs. Depends on `slices.Clone`, `invariants`, and error assertions for invalid internal-to-user conversions.

Integration points: Used by manifest metadata, compaction overlap checks, object info, span policies, blob mapping, and tests.

Risks: Inclusive/exclusive semantics are subtle, especially for internal sentinels at range ends. `Union` returns slices by reference, so callers needing ownership must clone.

Test signals: `key_bounds_test.go` covers boundary comparison, containment, overlap, validity, formatting, and union cases.
