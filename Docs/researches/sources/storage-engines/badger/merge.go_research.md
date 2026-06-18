<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/merge.go -->
# sources/storage-engines/badger/merge.go

## Purpose
This file implements Badger's per-key merge operator. It lets callers append merge operands as separate versions and periodically compact them into a single value using a caller-supplied merge function.

## Important APIs, Types, And Functions
`MergeOperator` stores the merge function, DB, key, close signal, and a read/write lock. `MergeFunc` merges an older value and newer accumulated value. `DB.GetMergeOperator` starts a background compaction goroutine. `iterateAndMerge` scans all versions for the key and applies the merge function. `compact` writes the merged value back with `bitDiscardEarlierVersions`. `runCompactions`, `Add`, `Get`, and `Stop` provide lifecycle and user operations.

## Control Flow
`Add` writes a normal transaction entry with the merge bit set. `Get` locks against background compaction and calls `iterateAndMerge` to synthesize a value on demand. `runCompactions` ticks at the configured duration and runs `compact`; on stop it runs one final compaction before exiting. `compact` ignores not-found or single-version states and asynchronously writes the merged value at the latest version key.

## State And Persistence Behavior
Each add creates a Badger version for the same logical key. Periodic compaction writes one merged value marked `bitDiscardEarlierVersions`, and normal LSM compaction can later drop older merge entries. Durability is the normal Badger write path; merge state is not stored separately from the key versions.

## Dependencies And Integration Points
The file uses transactions, key iterators with `AllVersions`, item metadata helpers, `NewEntry(...).withMergeBit`, `batchSetAsync`, key timestamp encoding in `y`, and `z.Closer`. It relies on LSM compaction in `levels.go` to eventually remove obsolete merged entries.

## Risks And Edge Cases
The merge function must be associative enough for version-order folding. `iterateAndMerge` stops at deleted/expired items and at `DiscardEarlierVersions`, so delete and compaction markers affect results. `compact` writes asynchronously, so errors are logged rather than returned to callers. `Stop` can block until the final compaction completes. The lock prevents concurrent `Get`/`compact` interleaving but not concurrent `Add` writes.

## Test Signals
`merge_test.go` covers not found before add, numeric and slice merges, immediate get before timer compaction, delete/reset behavior, get after stop, and old-version removal after close-triggered compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/merge.go -->
