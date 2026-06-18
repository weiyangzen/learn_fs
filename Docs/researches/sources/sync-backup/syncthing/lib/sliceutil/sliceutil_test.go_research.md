# sources/sync-backup/syncthing/lib/sliceutil/sliceutil_test.go

Purpose: covers the main invariant of `RemoveAndZero`.

Important tests: `TestRemoveAndZero` removes index 2 from `[1,2,3,4,5]`, expects the returned slice `[1,2,4,5]`, and scans the original backing array to ensure the removed value no longer remains.

State and persistence: in-memory only.

Dependencies and integration: uses Go `slices.Equal` and imports `sliceutil` as an external package, so it validates exported behavior.

Risks and signals: narrow but useful for order and zeroing. No coverage for pointer/reference element types, index panics, length-one slices, or `Map`.
