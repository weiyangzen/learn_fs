# sources/storage-engines/pebble/compaction_delete.go

## Purpose
`compaction_delete.go` implements Pebble's delete-only compaction kind. A delete-only compaction is a cheap space-reclamation operation driven by wide tombstone hints: if a range tombstone fully covers a table, Pebble can remove the whole table from the LSM, or, when the tombstone covers an edge span and virtual SSTables are available, excise the covered span and keep the remaining portion as a virtual table. Unlike normal compactions, it does not merge keys or write replacement data through the compaction runner.

## Important APIs, Types, And Functions
`tryScheduleDeleteOnlyCompaction` checks feature flags and concurrency, asks `d.mu.compact.wideTombstones.PickCompaction` for a candidate, constructs `newDeleteOnlyCompaction`, marks it in progress, and starts the common `DB.compact` lifecycle.

`newDeleteOnlyCompaction` creates a `tableCompaction` with `compactionKindDeleteOnly`, one input level containing the selected table, `deleteOnly` metadata from `tombspan.DeleteOnlyCompaction`, a no-op grant handle, a referenced current version, and bounds equal to the selected table's user-key bounds.

`runDeleteOnlyCompaction` produces the durable manifest edit. It either adds the selected table to `DeletedTables` and increments `TablesDeleted`, or calls `exciseTable`, applies the resulting left/right replacement through `applyExciseToVersionEdit`, increments `TablesExcised`, and annotates the compaction as `[excise]`.

`tombstoneKeyTypeFromKeys` converts a set of `keyspan.Key` tombstone kinds into the manifest key-type enum used by wide tombstone hinting, distinguishing point-range-delete-only, range-key-delete-only, and mixed cases.

## Control Flow
Scheduling requires delete-only compactions to be enabled, automatic compactions to be enabled, and `d.mu.compact.compactingCount` to be below the configured maximum compaction concurrency. Excise support is gated by `FormatVirtualSSTables` and the optional `EnableDeleteOnlyCompactionExcises` setting. The wide tombstone picker receives the current version and the excise-allowed flag, then returns either no candidate or a `tombspan.DeleteOnlyCompaction`.

Once launched, delete-only compactions use the same goroutine and event lifecycle as other table compactions through `DB.compact` and `compact1`. During execution, `runCompaction` dispatches `compactionKindDeleteOnly` to `runDeleteOnlyCompaction`. That function releases `DB.mu` while doing possible excise IO, constructs a `VersionEdit`, refreshes available disk bytes, and returns to the common manifest-application path in `compact1`.

For a full-table delete, no replacement table is created: the edit simply removes `{Level, FileNum}`. For an excise, the code validates the format version, calls `d.exciseTable` with tight bounds, rejects middle-of-table excises that would produce both left and right replacements, and applies the excise into the version edit. Delete-only excises therefore appear intended for tombstones covering a table prefix or suffix rather than splitting a table into two live fragments.

## State And Persistence Behavior
Delete-only compactions persist only manifest metadata changes. A full-table delete records the input table in `VersionEdit.DeletedTables`. An excise records deletion of the old table and addition of zero or one replacement virtual table, depending on `applyExciseToVersionEdit`. The underlying table backing may remain referenced by virtual metadata after an excise, so physical deletion is governed by version-set obsolete-file tracking after version installation.

The selected version is explicitly referenced in `newDeleteOnlyCompaction`, matching normal table compactions. Input table metadata is marked compacting through `AddInProgressLocked`, but `clearCompactingState` treats delete-only as special and resets inputs to not compacting on success because some delete-only operations can leave the file untouched, for example if loose bounds prevent a removal.

Metrics are stored in `c.metrics.perLevel` for the selected level. Full deletes increment `TablesDeleted`; excises increment `TablesExcised` and add a compaction annotation. No output blob list and no `compact.Stats` are produced.

## Dependencies And Integration Points
This file depends on the common compaction lifecycle from `compaction.go`, tombstone hint selection from `internal/tombspan`, range key/tombstone kinds from `internal/keyspan` and `internal/base`, manifest edit structures, and DB excise helpers. It is called before scheduler-mediated compactions in `maybeScheduleCompaction`, reflecting the expectation that delete-only compactions are cheap and reduce later compaction work.

It also interacts with options and format gates: `DisableAutomaticCompactions`, `private.disableDeleteOnlyCompactions`, `CompactionConcurrencyRange`, `FormatVirtualSSTables`, and `EnableDeleteOnlyCompactionExcises`.

## Risks
The delete-only path bypasses normal key merging, so the correctness of candidate selection is critical. `wideTombstones.PickCompaction` must only return tables whose contents are fully obsolete or safely excisable under the current snapshots, bounds, and format version.

Excise handling intentionally rejects middle excises. If the picker ever returns a candidate requiring both left and right replacements, this path fails with an assertion error rather than producing a two-sided split. Format gating is also strict: an excise candidate below `FormatVirtualSSTables` panics.

Because delete-only compactions are scheduled outside `CompactionScheduler`, their concurrency check is a direct count against `maxConcurrency`. The loop in `maybeScheduleCompaction` can start multiple delete-only compactions as long as capacity remains, so wide tombstone picker overlap checks and compacting-state markings must prevent duplicate or conflicting deletes.

## Test Signals
Useful tests should cover full-table deletion, prefix/suffix excise, snapshots that prevent deletion, mixed point/range tombstone hint types, disabled feature flags, disabled automatic compactions, concurrency saturation, and format-version gating. `compaction_delete_test.go` provides datadriven coverage for hint collection, scheduling, excise annotations, LSM descriptions, snapshot closure, ingest interactions, and resulting compaction summaries.
