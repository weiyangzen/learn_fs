# sources/storage-engines/rocksdb/db/c_test.c

## Purpose
This file is RocksDB's broad C API regression and smoke test for `rocksdb/c.h`. It is a single C translation unit that opens real temporary RocksDB instances, exercises nearly every exported C wrapper family, verifies data-path behavior with direct assertions, and checks that wrapper-owned handles can be created, queried, and destroyed without obvious ABI or lifetime regressions.

The suite is intentionally end-to-end rather than mock-driven. It validates database creation, backup/restore, checkpoints, external SST ingestion, write batches, iterators, pinned reads, multi-get variants, column families, prefix/filter behavior, option getter/setter parity, transactions, optimistic transactions, secondary instances, statistics, wait-for-compact, write buffer management, remote compaction service callbacks, SST file manager settings, and final background-work cancellation.

## Important APIs, Types, And Helpers
The test imports only the public C API header, `rocksdb/c.h`, plus standard C/POSIX headers. Its helper layer includes:

- `StartPhase`, `CheckNoError`, `CheckCondition`, `CheckEqual`, `Free`, `CheckValue`, and `CheckPinnedValue`, which make phase-tagged failures abort immediately.
- `CheckGet`, `CheckGetCF`, `CheckPinGet`, and `CheckPinGetCF`, which wrap normal and pinned point lookup checks.
- `CheckMultiGetValues`, `CheckIter`, and write-batch callback validators (`CheckPut`, `CheckDel`, `CheckPutCF`, `CheckDelCF`, `CheckMergeCF`, `CheckLogData`).
- Custom callback implementations for comparator (`CmpCompare`/`CmpName`), compaction filter and factory (`CFilterFilter`, `CFilterCreate`), merge operator (`MergeOperatorFullMerge`, `MergeOperatorPartialMerge`), and remote compaction service (`RemoteCompactionSchedule`, `RemoteCompactionWait`, `RemoteCompactionCancel`, `NullSchedule`).
- `CheckMetaData`, `GetAndCheckMetaData`, and `GetAndCheckMetaDataCf`, which validate column-family metadata, level metadata, and SST file metadata returned through the C wrappers.
- `LoadAndCheckLatestOptions`, which loads persisted options from a DB, checks expected column-family names/options, and verifies reopening with the loaded options.

The `main` function creates and destroys many C API handle types: `rocksdb_t`, `rocksdb_options_t`, `rocksdb_readoptions_t`, `rocksdb_writeoptions_t`, `rocksdb_compactoptions_t`, `rocksdb_cache_t`, `rocksdb_env_t`, `rocksdb_dbpath_t`, `rocksdb_checkpoint_t`, `rocksdb_backup_engine_t`, `rocksdb_writebatch_t`, `rocksdb_writebatch_wi_t`, `rocksdb_iterator_t`, `rocksdb_column_family_handle_t`, `rocksdb_transactiondb_t`, `rocksdb_transaction_t`, `rocksdb_optimistictransactiondb_t`, table/filter/compaction/backup/statistics/memory/remote-compaction option wrappers, and factory wrappers.

## Control Flow
The program is a linear phase-driven test. Temporary path names are derived from `TEST_TMPDIR` or `/tmp`/`TEMP` and a process/user-derived test id, then each `StartPhase` block mutates the DB or a wrapper object and validates expected results before moving on.

Early phases construct base options, a custom comparator, block-based table options, LRU cache, default env, rate limiters, read/write/compact options, and the base DB. Basic persistence phases then destroy/open the DB, put and get `foo`, create backups, restore from the latest backup, compare DB identities, create checkpoints, test DB identity behavior when `write_dbid_to_manifest` is enabled, and export/import a column family through checkpoint metadata.

Middle phases exercise data operations. Compaction APIs are run over full and bounded ranges. Cache usage is checked after pinning data through an iterator. External SST files are written with `rocksdb_sstfilewriter_t`, ingested, overwritten, and cleaned up. WriteBatch and WriteBatchWithIndex coverage includes put/delete/delete-range, vectored key/value APIs, savepoints, serialized representation round trips, indexed reads from batch plus DB, batch iterators over base DBs, and read-option bounds.

Iterator/read phases verify first/last/next/prev/seek/seek-for-prev, slice-returning iterator APIs, ordinary multi-get, pinned zero-copy reads, `rocksdb_get_into_buffer`, approximate sizes, property reads, snapshots, snapshot behavior with in-place memtable updates, repair, filters using Bloom/Ribbon policies, compaction filters/factories, merge operator behavior, and prefix seek behavior with plain table/hash skiplist configuration.

Column-family coverage creates, lists, opens, writes, deletes, range-deletes, flushes, multi-gets, batched multi-gets, slice-based batched multi-gets, pinned CF reads, `key_may_exist`, CF iterators, multi-CF iterator creation, metadata inspection, CF-specific DB paths, option loading, and dropped-CF cleanup.

The large options section checks many `rocksdb_options_t` setters/getters, makes an independent copy, then mutates the copy to confirm fields are copied rather than aliased. Separate phases cover read, write, compact, flush, cache, allocator, logger, env, universal compaction, FIFO compaction, backup-engine, and compression options.

Transaction phases open TransactionDBs and OptimisticTransactionDBs, exercise direct DB reads/writes, transactional reads/writes/deletes, pinned reads, multi-get, transaction names, WAL log data scanning via `rocksdb_get_updates_since`, snapshots, iterators, rollback, savepoints, column families, memory usage, WAL/CF flushes, two-phase prepare/commit/rollback recovery, `multi_get_for_update` lock conflicts, write-prepared policy, and optimistic transaction reopen with column families.

Late phases test memtable representation selection, secondary DB catch-up, DB paths, prefix-seek filters, statistics ticker/histogram access, wait-for-compact options, wait-for-compact execution, write buffer manager fields, remote compaction callback installation/fallback behavior, scheduler response wrappers, compaction service options override setters, checksum/SST partitioner factories on regular options, null remote callback handling, cancellation flag wrappers, SST file manager settings, duplicate-column-family error returns, `rocksdb_cancel_all_background_work`, and final handle destruction.

## State And Persistence Behavior
The file creates real on-disk RocksDB state under temporary directories. It repeatedly destroys and recreates `dbname`, creates separate backup/checkpoint/SST/DB-path/secondary/import/export paths, and uses actual WAL, SST, MANIFEST, checkpoint, backup, and column-family metadata side effects as test evidence.

Persistence-sensitive checks include restore retaining `"foo"`, checkpoint and backup DB identity changes, manifest-stored DB identity remaining stable across checkpoint reopen, external SST ingestion materializing keys, metadata reporting non-empty levels/files, write batch WAL log data being discoverable after commit, prepared transactions surviving DB reopen, secondary DB catch-up seeing primary writes, and statistics counters/histograms changing after writes. Most allocated C API return values are explicitly freed or destroyed, which is part of the wrapper contract under test.

## Dependencies And Integration Points
This file is integrated with RocksDB's C binding layer and indirectly with many C++ subsystems: DB open/close/destroy/repair, Env, Cache, block-based/plain/cuckoo table factories, filters, prefix extractors, compaction, backup engine, checkpoints, external SST ingestion, metadata, WriteBatch, WriteBatchWithIndex, snapshots, WAL iteration, TransactionDB, OptimisticTransactionDB, memory accounting, statistics, remote compaction service, file checksum factories, SST partitioners, and SST file manager.

Because it includes only `rocksdb/c.h`, it is an ABI-facing test: new C wrappers are often wired into this file to prove they compile from C, expose sensible ownership semantics, map options correctly, and interoperate with the underlying C++ implementation.

## Risks And Edge Cases
The test is large and linear, so earlier option mutations can leak into later phases if not reset carefully. Several phases rely on precise data-path side effects such as Bloom/Ribbon false-positive counters, non-empty metadata after compaction/flush, DB identity length, or platform-specific allocator support. Temporary path handling uses fixed-size 200-byte buffers and process-derived names; unusually long `TEST_TMPDIR` paths can stress these buffers.

Resource lifetime is a major risk area. The file tests many ownership boundaries, but any missed destroy/free can hide in the long happy path. Conversely, destroying a factory or logger too early would expose wrapper ownership bugs. Remote compaction coverage intentionally falls back to local compaction; it validates callback plumbing rather than a real serialized remote compaction result.

## Test Signals
The primary signal is the process printing `PASS` after every phase completes without aborting. Failures include phase names in stderr. Meaningful sub-signals include successful DB reopen after loaded options, expected point lookup results after each mutation, expected CF list sizes/names, expected metadata invariants, option getter values matching setters and independent copies, expected transaction conflict/prepared-transaction behavior, non-zero statistics after writes, remote compaction schedule/wait counters, and `create_column_family` returning `NULL` with an error for duplicate names.
