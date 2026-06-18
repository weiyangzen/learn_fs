<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/mid_key.go -->
## sources/storage-engines/pebble/mid_key.go

Purpose: implements `DB.ApproximateMidKey`, which returns an approximate key that bisects estimated disk usage within a key range using SST metadata and index blocks rather than data blocks.

Important APIs and types: `ApproximateMidKey(ctx, kr, epsilon)` returns `midKey`, estimated left-side size, and error. Internal helpers are `midKeySST`, `collectMidKeySSTs`, `resolveEdgeSizes`, `findMidKey`, and `mergeWalkStraddlers`.

Control flow: the public method validates DB open state and range order, loads the read state, collects overlapping SSTs across L0 sublevels and lower levels, resolves partial edge SST sizes until uncertainty is bounded by `2*epsilon`, rejects ranges too small relative to epsilon, then finds a mid key. `findMidKey` sorts SSTs by upper bound, accumulates effective sizes, returns an SST upper bound if within epsilon, or refines overshooting SSTs through `mergeWalkStraddlers`. The merge walk reads block index entries for sufficiently large straddlers and advances the smallest separator across files until the size deficit is reached.

State and persistence: no mutation or persistence. It reads current version metadata and index blocks through the file cache.

Dependencies and integration: depends on manifest table metadata, version overlap iteration, file-cache `estimateSize` and `collectBlockEntries`, sstable block entries, Pebble comparer, and `EstimateDiskUsage` semantics.

Risks and edge cases: result is approximate and may be nil for empty, tiny, or poorly splittable ranges. Edge-size scaling uses table size ratios for reference-inclusive size estimates. L0 is handled specially to avoid transitive bound expansion. Rounding can consume all SSTs without finding a key.

Test signals: `mid_key_test.go` exercises empty spans, tiny ranges, single SST, multiple L0 SSTs, multiple levels, and tight epsilon.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/mid_key.go -->
