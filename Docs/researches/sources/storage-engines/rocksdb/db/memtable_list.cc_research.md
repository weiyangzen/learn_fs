# sources/storage-engines/rocksdb/db/memtable_list.cc

## Purpose
`memtable_list.cc` implements immutable memtable list management for a column family. It serves reads from sealed memtables, tracks copy-on-write list versions used by SuperVersion readers, selects memtables for flush, installs flush results into the MANIFEST in recovery-safe order, retains flushed memtable history for transactions, and supports atomic flush across column families.

## Important APIs, types, and functions
Top-level scan helpers `MultiScanOverlapsUserKeyRange`, `MultiScanIteratorOverlapsUserKeyRange`, and `MultiScanIntersectsMemTable` conservatively decide whether a bounded multi-scan can skip an immutable memtable.

`MemTableListVersion` implements `AddMemTable`, `UnrefMemTable`, copy construction with refcount bumps, `Ref`, `Unref`, `Get`, `MultiGet`, `GetMergeOperands`, `GetFromHistory`, `GetFromList`, `AddRangeTombstoneIterators`, iterator addition, aggregate stats, earliest/first sequence queries, `Add`, `Remove`, history trimming, memory-limit checks, and newest UDT selection.

`MemTableList` implements flush state (`IsFlushPending`, `IsFlushPendingOrRunning`), `PickMemtablesToFlush`, `RollbackMemtableFlush`, `TryInstallMemtableFlushResults`, `Add`, `TrimHistory`, cached memory/history values, `InstallNewVersion`, `RemoveMemTablesOrRestoreFlags`, `PrecomputeMinLogContainingPrepSection`, secondary-replay cleanup via `RemoveOldMemTables`, and `GetEditForDroppingCurrentVersion`.

The free function `InstallMemtableAtomicFlushResults` installs multiple column-family flush results as one atomic MANIFEST group.

## Control flow
Reads search immutable memtables newest-to-oldest. `GetFromList` calls each memtable's `Get` with `immutable_memtable=true`, preserving the first visible sequence number and continuing through merge-in-progress statuses until a final value/deletion/error is found or lists are exhausted. `MultiGet` delegates to each memtable and stops once the range is empty. Iterator creation optionally probes bounded scan ranges and adds point and range-tombstone iterators to `MergeIteratorBuilder`.

Adding an immutable memtable calls `InstallNewVersion`, inserts at the front of the list, increments `num_flush_not_started_`, sets `imm_flush_needed` when transitioning from zero pending memtables, trims history if needed, and refreshes cached memory/history flags.

Flush picking iterates from oldest to newest so flush jobs receive increasing memtable IDs. It marks unstarted memtables as in progress, decrements `num_flush_not_started_`, tracks max next WAL number, and avoids selecting non-consecutive memtables when an in-progress flush is sandwiched between candidates.

Flush result installation first marks the flushed memtables complete with a file number. Only one thread enters the MANIFEST commit loop through `commit_in_progress_`. It repeatedly commits the oldest contiguous completed memtables, computes WAL recovery edits, writes `VersionEdit`s through `VersionSet::LogAndApply`, and removes or restores flags in the callback. This preserves FIFO MANIFEST order even when newer flush jobs finish first.

Atomic flush marks all participating memtables complete, builds per-CF edit lists, computes WAL retention for 2PC or non-2PC recovery, marks edits as an atomic group when multiple CFs participate, logs them through `VersionSet::LogAndApply`, then removes memtables or rolls back flags across all lists.

## State and persistence behavior
`MemTableListVersion` is a refcounted immutable view. Mutations install a new version if readers still hold the old one. Unflushed memtables live in `memlist_`; flushed history lives in `memlist_history_` when `max_write_buffer_size_to_maintain_` is positive. Memory accounting is pushed into the parent `MemTableList` usage counter and cached in atomics.

Persistence state is mediated by memtable `VersionEdit`s, file numbers, WAL numbers, `LogsWithPrepTracker`, `VersionSet`, and MANIFEST `LogAndApply`. On success, memtables are marked flushed and either moved to history or unreferenced. On failure or dropped-column-family cases, flags and edits are restored so data remains readable or flushable.

## Dependencies and integration points
This file integrates `ColumnFamilyData`, `VersionSet`, `DBImpl` recovery helpers, `LogsWithPrepTracker`, `RangeDelAggregator`, `MergeIteratorBuilder`, `LogBuffer`, `ThreadStatus`, `FSDirectory`, `FlushJobInfo`, scan range options, snapshots, and test sync points. It is on the critical path for DB reads, flush scheduling, atomic flush, WAL deletion, transaction validation, secondary log replay, and iterator construction.

## Risks and edge cases
Ordering is the main risk. MANIFEST commits must match memtable creation order, even with parallel flush completion. Rollback must restore only appropriate completed or in-progress flags. Dropped column families cannot lose in-memory data before their generated files are discoverable. History trimming must respect refcounts and memory budgets. Scan pruning is conservative because iterator errors, empty probes, and range deletions all force overlap. Copy-on-write versions require external DB mutex discipline.

## Test signals
`memtable_list_test.cc` exercises empty lists, point reads across immutable memtables, history lookups and trimming, flush pending/picking/rollback, out-of-order flush completion, atomic flush across CFs, and user-defined timestamp tracking. Broader signals include flush job, DB open/recovery, transaction validation, secondary instance, atomic flush, range deletion, MultiGet, and iterator tests.
