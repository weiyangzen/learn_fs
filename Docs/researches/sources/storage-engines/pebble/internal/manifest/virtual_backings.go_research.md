<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/virtual_backings.go -->
# sources/storage-engines/pebble/internal/manifest/virtual_backings.go

Purpose: implements `VirtualBackings`, the manifest-side state holder for physical table backings that are referenced by virtual sstables in the latest version. It tracks backing membership by `base.DiskFileNum`, virtual table usage, protection counts used by concurrent external ingestion, aggregate stats by placement, unused backings, and local rewrite candidates.

Important APIs and types: `MakeVirtualBackings`, `AddAndRef`, `Remove`, `AddTable`, `RemoveTable`, `Protect`, `Unprotect`, `Stats`, `Usage`, `Unused`, `Get`, `All`, `DiskFileNums`, `ReplacementCandidate`, `String`; internal `backingWithMetadata` and `virtualBackingRewriteCandidatesHeap`.

Control flow and state: adding a backing takes a ref, inserts it into `m`, records placement stats, and marks it unused until protected or used by a virtual table. `AddTable` validates `TableMetadata.Virtual`, increments `virtualizedSize`, records `tableAndLevel`, removes the backing from `unused`, and pushes or fixes the local-only heap. `RemoveTable` subtracts size, re-adds to `unused` if no virtual tables or protections remain, and removes/fixes heap membership. `Protect` and `Unprotect` maintain `protectionCount`, preventing a backing from being returned by `Unused`.

Persistence and integration: this is in-memory manifest/version bookkeeping; persistence happens indirectly through version edits that add/remove backing tables and table refs. It integrates with `TableBacking`, `TableMetadata`, `base.Placement`, `metrics.CountAndSizeByPlacement`, and compaction/rewrite logic that asks for replacement candidates. Risks include invariant-sensitive ref lifecycle, panics on unknown/duplicate state, heap index correctness, division by zero if a zero-size backing were admitted, and the assumption that only local backings are rewrite candidates. Test signals come from datadriven coverage in `virtual_backings_test.go`.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/internal/manifest/virtual_backings.go -->
