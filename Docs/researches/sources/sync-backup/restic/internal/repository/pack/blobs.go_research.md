
# sources/sync-backup/restic/internal/repository/pack/blobs.go

Purpose: defines `Blobs`, a slice of pack `Blob` entries, with a single `Sort` method ordering entries by offset.

The control flow is intentionally small: `Sort` uses `slices.SortFunc` and `cmp.Compare` on `Offset`. Sorting is required before streaming sections of a pack so the loader can read contiguous ranges, skip gaps, and detect overlapping entries.

There is no persistence in this file; it provides an ordering invariant for pack operations. Integration points include `Repository.LoadBlobsFromPack`, `streamPack`, pack tests, and prune/repack paths that pass sets of blobs by pack. Risks are limited but important: incorrect sorting would make range coalescing fail or cause false overlap errors. `blobs_test.go` verifies sorted offsets and nil-slice tolerance.
