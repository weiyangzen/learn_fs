# sources/storage-engines/leveldb/db/db_impl.cc

## Purpose
This is LevelDB's central `DB` implementation. It coordinates option sanitization, DB creation/open/recovery, write-ahead logging, memtable and immutable memtable state, snapshots, reads, write batching, L0 flushing, background/manual compaction, file garbage collection, properties, approximate sizes, destruction, and the public `DB::Open`/`DestroyDB` entry points.

## Important APIs, Types, And Functions
Internal structs `DBImpl::Writer`, `CompactionState`, `CompactionState::Output`, and `ManualCompaction` model write queue entries and in-flight compactions. Major functions include `SanitizeOptions`, `NewDB`, `Recover`, `RecoverLogFile`, `WriteLevel0Table`, `CompactMemTable`, `CompactRange`, `MaybeScheduleCompaction`, `BackgroundCompaction`, `DoCompactionWork`, `NewInternalIterator`, `Get`, `NewIterator`, `Write`, `BuildBatchGroup`, `MakeRoomForWrite`, `GetProperty`, `GetApproximateSizes`, `DB::Open`, and `DestroyDB`.

## Control Flow
Open creates a `DBImpl`, locks the DB, creates or recovers the manifest, replays eligible logs into memtables, optionally reuses the last log, creates a new log/memtable if needed, writes recovered manifest edits, removes obsolete files, and schedules compaction. Writes enter a FIFO writer queue, optionally group compatible batches, reserve sequence numbers, append to the WAL, optionally sync, insert into `mem_`, publish `LastSequence`, and wake queued writers. `MakeRoomForWrite` delays near L0 soft limits, waits on immutable memtables and L0 hard limits, or rotates to a new log and immutable memtable before scheduling background compaction.

## State And Persistence Behavior
Persistent state is the DB directory: `CURRENT`, `LOCK`, `LOG`, `MANIFEST-*`, `.ldb/.sst` tables, and temp files. `pending_outputs_` protects files being built from deletion. Manifest changes are installed via `VersionSet::LogAndApply`; log replay writes memtables to L0 when recovery memory exceeds `write_buffer_size`. Sync write failures and log close failures record `bg_error_`, after which future writes fail and obsolete file deletion is suppressed. Snapshots pin sequence visibility; iterators pin `mem_`, `imm_`, and the current `Version`.

## Dependencies And Integration Points
The file is tied to `MemTable`, `VersionSet`, `VersionEdit`, `Compaction`, `TableCache`, table `BuildTable`, `log::Reader`/`Writer`, `WriteBatchInternal`, `DBIter`, `filename` helpers, Env file APIs, comparators, filter policies, block/table builders, merging iterators, snapshots, and logging. Public methods implement the `leveldb::DB` contract and expose test hooks used heavily by `db_test.cc` and corruption tests.

## Risks And Edge Cases
This file is concurrency and crash-recovery critical. Risks include write group sequence assignment, WAL sync uncertainty, log reuse recovery, stale-file deletion after failed manifest writes, compaction output installation order, snapshot-aware version dropping, deletion-marker elision only at base level, L0 write stalls, manual compaction range progress, shutdown races, and iterator lifetime pinning. `MaybeIgnoreError` deliberately masks some errors unless `paranoid_checks` is set.

## Test Signals
`db_test.cc`, `corruption_test.cc`, and `fault_injection_test.cc` directly validate most surfaces: open options, locking, recovery, large logs, log reuse, sync/log-close/manifest errors, missing SST files, compaction output cleanup, snapshots, iterators, bloom filters, multithreaded writes, randomized model comparison, and crash-like unsynced file loss.
