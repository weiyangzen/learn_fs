# Research: sources/storage-engines/rocksdb/db/c.cc

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-008570`: lines 1-7443, `Docs/researches/chunks/subset-b-008570_research.md`
- `subset-b-008571`: lines 7444-8988, `Docs/researches/chunks/subset-b-008571_research.md`

## Chunk Research

### subset-b-008570: lines 1-7443

# sources/storage-engines/rocksdb/db/c.cc lines 1-7443

## Scope

This chunk is the first 7,443 lines of RocksDB's C API implementation. It begins at the file header and `#include "rocksdb/c.h"`, enters `extern "C"`, defines most opaque C handle structs, implements callback adapter classes, and exposes a large surface of DB, backup, checkpoint, column-family, read/write, iterator, write-batch, options, cache, environment, SST writer, ingestion, live-file, and metadata wrappers. The chunk ends inside the declaration of `rocksdb_sst_file_metadata_destroy`; the remaining SST metadata accessors and later APIs are outside this chunk.

## Purpose

The code translates the C ABI declared by `rocksdb/c.h` into calls on RocksDB's C++ API. It hides C++ objects behind small C structs containing raw pointers or value members, converts C buffers into `Slice`/`std::string`/vectors, converts `Status` to heap-allocated C error strings, and maps user-supplied C callbacks into C++ virtual interfaces such as `Comparator`, `CompactionFilter`, `MergeOperator`, `SliceTransform`, `Logger`, `EventListener`, and `CompactionService`.

## Important Types And Ownership

- `rocksdb_t`, `rocksdb_backup_engine_t`, `rocksdb_iterator_t`, `rocksdb_wal_iterator_t`, `rocksdb_sstfilewriter_t`, transaction-related wrappers, and checkpoint wrappers generally own raw C++ pointers and destroy them in matching `*_destroy`/`*_close` functions.
- Option wrappers such as `rocksdb_options_t`, `rocksdb_readoptions_t`, `rocksdb_writeoptions_t`, `rocksdb_compactoptions_t`, `rocksdb_block_based_table_options_t`, `rocksdb_cuckoo_table_options_t`, `rocksdb_flushoptions_t`, and compaction-option wrappers hold C++ option values by value.
- Shared-resource wrappers (`rocksdb_logger_t`, checksum/partitioner/table collector factories, cache, write buffer manager, SST file manager, rate limiter, memory allocator) hold `std::shared_ptr` so they can be installed into options without requiring immediate destruction of the underlying C++ object.
- `rocksdb_column_family_handle_t` tracks an `immortal` flag. The default column family handle returned by `rocksdb_get_default_column_family_handle` points into the DB and is not deleted; other handles are deleted by `rocksdb_column_family_handle_destroy`.
- `rocksdb_readoptions_t` stores `Slice` members for upper/lower iterator bounds, timestamp, and iterator start timestamp. These are backing storage for pointers inside `ReadOptions`; callers must keep the source buffers valid according to RocksDB expectations because the `Slice` only references external memory.
- Metadata wrappers at the end of the chunk store pointers into parent metadata containers: `rocksdb_level_metadata_t` points into `rocksdb_column_family_metadata_t::rep.levels`, and `rocksdb_sst_file_metadata_t` points into a level's `files`. Destroying the parent before children leaves dangling references.

## Callback Adapter APIs

- `rocksdb_compactionfilter_t` subclasses `CompactionFilter`; `Filter` calls a C callback and may assign a replacement value. Its destructor invokes the user destructor. It also exposes `IgnoreSnapshots`.
- `rocksdb_compactionfilterfactory_t` subclasses `CompactionFilterFactory` and creates per-compaction `rocksdb_compactionfilter_t` instances from a C factory callback.
- `rocksdb_comparator_t` subclasses `Comparator`, supports normal comparison plus optional timestamp comparison and timestamp-stripped comparison. Key shortening methods are no-ops in the C binding.
- `rocksdb_filterpolicy_t` is a base C-visible filter wrapper. Built-in bloom and ribbon constructors create local C++ wrapper subclasses that delegate to `NewBloomFilterPolicy` or `NewRibbonFilterPolicy`.
- `rocksdb_mergeoperator_t` bridges C full and partial merge callbacks. It builds operand pointer/length arrays, assigns the returned value into RocksDB output, then frees it through either the provided `delete_value_` callback or `free`.
- `rocksdb_slicetransform_t` bridges prefix transform callbacks. Built-in fixed-prefix and noop transforms are wrapped by `SliceTransformWrapper`.
- `rocksdb_callback_logger_t` subclasses `Logger`, formats `Logv` output into a stack buffer or heap buffer, and calls the C logging callback with level and bytes.
- `rocksdb_eventlistener_t` subclasses `EventListener` and forwards flush, compaction, subcompaction, external ingestion, background error, stall condition, and memtable sealed events. It creates short-lived stack `rocksdb_t` wrappers around `DB*` for event callbacks and reinterprets RocksDB event-info structs as C wrapper types.
- `rocksdb_compactionservice_t` subclasses `CompactionService`, forwards scheduling/wait/cancel/installation events to C callbacks, validates schedule responses, and installs itself into `Options::compaction_service` through a `shared_ptr`.

## Main DB Control Flow

- Opening APIs allocate C++ DB objects with `DB::Open`, `DBWithTTL::Open`, `DB::OpenForReadOnly`, and `DB::OpenAsSecondary`, then release the resulting `unique_ptr` into `rocksdb_t`.
- Column-family open variants build `std::vector<ColumnFamilyDescriptor>` from C arrays, return one `rocksdb_column_family_handle_t` per returned C++ handle, and wrap the DB pointer. TTL opens also build a `std::vector<int32_t>` of TTLs.
- `rocksdb_open_and_trim_history` wraps `DB::OpenAndTrimHistory` and returns handles for every opened column family.
- `rocksdb_close` deletes both the C++ `DB` and the C wrapper.
- `rocksdb_try_catch_up_with_primary` exposes secondary catch-up via `DB::TryCatchUpWithPrimary`.
- `rocksdb_destroy_db` and `rocksdb_repair_db` forward to `DestroyDB` and `RepairDB`.

## Read/Write APIs

- Point writes (`rocksdb_put`, `rocksdb_put_cf`, `rocksdb_put_with_ts`, `rocksdb_delete*`, `rocksdb_singledelete*`, `rocksdb_merge*`) wrap key/value/timestamp buffers in `Slice` and call the matching `DB` method.
- `rocksdb_write` writes a `WriteBatch`; `rocksdb_write_writebatch_wi` writes the underlying `WriteBatch` from a `WriteBatchWithIndex`.
- Gets use either `PinnableSlice` or `std::string`, set output lengths on success, return `nullptr` on not found without setting an error, and use `CopyString` to allocate returned data with `malloc`.
- Timestamped get and multiget variants return value and timestamp buffers separately.
- `rocksdb_multi_get*` builds arrays/vectors of `Slice`, column-family handles, `PinnableSlice`/`std::string`, and `Status`. Per-key errors are returned as `strdup` strings except not-found, which is reported as null value and null error.
- Batched multiget variants return `rocksdb_pinnableslice_t` objects to avoid copying values; the slice-based variant reinterprets `rocksdb_slice_t` as `Slice`, relying on identical memory layout.
- `rocksdb_key_may_exist*` optionally returns copied value data only when RocksDB reports the value was actually found.

## Iterators, WAL, Snapshots, And Properties

- Iterator wrappers expose construction for default and column-family iterators, multi-CF iterator creation, seek/next/prev, validity, status, refresh, and direct key/value/timestamp access. Direct accessors return pointers into the iterator's current state; caller must not retain them after iterator movement/destruction.
- `rocksdb_iter_key_slice`, `rocksdb_iter_value_slice`, and `rocksdb_iter_timestamp_slice` return a C `rocksdb_slice_t` view for lower overhead.
- WAL iteration uses `DB::GetUpdatesSince`, then exposes valid/next/status/destroy and `rocksdb_wal_iter_get_batch`, which moves the WAL batch into a newly created `rocksdb_writebatch_t`.
- Snapshot wrappers call `GetSnapshot`, `ReleaseSnapshot`, and `GetSequenceNumber`; snapshots are owned by the DB until released.
- Property APIs expose string and integer DB/column-family properties using `GetProperty` and `GetIntProperty`.
- Size and maintenance APIs include approximate sizes, approximate sizes with flags, live-file metadata, manual compaction, suggested compaction, flush, WAL flush, file deletion disable/enable, and delete-files-in-range.

## WriteBatch And WriteBatchWithIndex

- `rocksdb_writebatch_create*` constructs standard batches, including serialized-data and parameterized constructors.
- Mutation methods cover put, merge, delete, single delete, delete range, timestamped variants, column-family variants, and vectorized `SliceParts` variants.
- Iteration uses local `WriteBatch::Handler` subclasses (`H` and `HCF`) to call C callbacks for put/delete/merge and optional log data.
- Save-point functions expose `SetSavePoint`, `RollbackToSavePoint`, and `PopSavePoint`.
- Timestamp update functions call `WriteBatch::UpdateTimestamps` with a C callback that maps column-family id to timestamp size.
- `rocksdb_writebatch_wi_*` mirrors the mutation surface for `WriteBatchWithIndex`, adds indexed reads from batch or batch+DB, pinned reads, and iterators overlaying a base iterator. The overlay constructors delete the passed base iterator wrapper after transferring its `Iterator*` into the new iterator.

## Backup, Restore, Checkpoint, And External Files

- Backup engine wrappers open backup engines from DB options or explicit backup options, create backups, purge old backups, verify backups, restore latest/specific backups, expose backup info fields, stop backups, and close engines.
- Backup option setters/getters cover backup dir, environment, file sharing, sync, old-data destruction, WAL backup, rate limits/limiters, background operations, callback trigger interval, max backups to open, and checksum naming mode.
- Checkpoint wrappers create a checkpoint object, create a checkpoint directory, export a column family, and destroy the checkpoint.
- Export/import metadata appears in wrappers for checkpoint export and `rocksdb_create_column_family_with_import`; its ownership is represented by `rocksdb_export_import_files_metadata_t`, with destruction likely implemented outside this chunk.
- `SstFileWriter` wrappers create writers, open files, add/put/merge/delete/delete-range records, finish, get file size, and destroy.
- External file ingestion options expose move-files, snapshot consistency, global sequence number, blocking flush, ingest-behind, and bottommost-level checks; ingestion functions forward a C file-list array into a `std::vector<std::string>`.

## Options And Resource Configuration

- `rocksdb_options_t` creation, copy, destroy, preset optimizers, dynamic `SetOptions`, and `GetOptionsFromString` are exposed.
- Table-related configuration includes block-based table options, cuckoo table options, plain table factory, bloom/ribbon filter policies, block caches, metadata cache pinning tiers, checksum, block sizes, index/search types, filter caching, and block alignment.
- Core DB/CF options setters/getters cover create flags, paranoid checks, file opening, path vectors, env/loggers, write buffers/managers, SST file manager, max open files, WAL size/ttl/dir, file sizes, level sizing, compaction triggers, compression, bottommost compression options, prefix extractor, direct IO/mmap/fsync, stats periods, concurrency, background jobs, log retention, pending compaction limits, manifest size, table cache shards, memtable factory/options, identity/DBID/WAL tracking in manifest, merge limits, bloom locality, inplace update, compaction style/priority, universal/FIFO compaction, rate limiter, atomic/manual WAL flush, WAL compression, and compact-on-deletion collectors.
- Blob options in this chunk expose enabling blob files, min/blob file size, blob compression, garbage collection, read-triggered compaction threshold, compaction wakeup, blob compaction readahead, starting level, blob cache, and prepopulate mode.
- Statistics wrappers enable statistics, clamp/set/get stats level, stringify statistics, read ticker counts, and fill histogram data.
- `ReadOptions`, `WriteOptions`, `CompactRangeOptions`, and `FlushOptions` have create/destroy plus many direct setters/getters. Read options include checksum/cache/snapshot/bounds/read-tier/tailing/readahead/prefix/total-order/max-skippable/background-purge/range-deletion/deadline/io-timeout/async-io/multiget optimization/timestamp/iter-start-ts/auto-readahead. Write options include sync, WAL disable, missing CF ignore, no slowdown, low priority, and memtable insert hint. Compact options include bottommost compaction, exclusivity, level targeting, write stall permission, subcompactions, and full-history timestamp lower bound.

## Cache, Env, And Memory Utilities

- Cache wrappers create LRU and HyperClock caches, optionally with strict capacity or option structs; expose capacity, usage, pinned usage, table address count, occupancy count, disown-data, and capacity mutation.
- Memory allocator wrapper creates a jemalloc nodump allocator through `NewJemallocNodumpAllocator`.
- `WriteBufferManager` wrappers create managers with or without a cache, expose enabled/cost/memory metrics, buffer size mutation, and allow-stall mutation.
- `SstFileManager` wrappers create managers, set max space and compaction buffer, read space/deletion/trash metrics, and configure delete rate/trash ratio.
- Env wrappers create default and in-memory envs, control thread-pool sizes by priority, join threads, lower IO/CPU priority, create directories, and destroy non-default envs only.

## State And Persistence Behavior

- Persistent DB state is modified through writes, write batches, column-family create/drop/import, compaction, flush, WAL flush, file deletion, repair/destroy, external file ingestion, backup/restore, checkpoints, and SST writer output.
- Options objects are in-memory configuration until used to open a DB or installed into another option object. Some runtime options can be changed on an open DB through `rocksdb_set_options*`.
- Returned heap buffers use mixed allocation conventions: many data strings use `malloc` via `CopyString`, human-readable strings often use `strdup`, and C++ wrappers use `new`. Callers must use the corresponding C API free/destroy functions from the broader C binding.
- Several APIs return non-owning pointers into live C++ objects (`Iterator` key/value/timestamp slices, live-file strings, job-info strings, metadata child wrappers). Their lifetime is tied to the parent iterator/event info/livefiles/metadata object.
- Shared pointers transfer ownership for some callback-derived objects when installed in options (`merge_operator`, compaction filter factory, prefix extractor, event listener, compaction service). Destroying the original C wrapper after installing it can double-delete unless the API contract says ownership was transferred.

## Dependencies And Integration Points

- Primary dependencies are RocksDB C++ headers for DB core, options, env, listeners, backup/checkpoint utilities, transaction/write-batch utilities, memory/cache/rate-limit utilities, table factories, and statistics/perf context.
- The file is the implementation backing `rocksdb/c.h`, so ABI stability, symbol names, allocation conventions, and enum integer mappings are integration-critical for C, Go, Rust, Python, and other FFI consumers.
- It integrates with RocksDB's callback-based extension points by subclassing C++ abstract classes and forwarding to C function pointers.
- It integrates with persistence subsystems: WAL/log iteration, backup engine, checkpoint/export/import, SST file writer, external ingestion, live file metadata, and DB identity.
- It integrates with runtime observability through statistics, perf context, properties, event listeners, logger callbacks, compaction/flush/write-stall/memtable info accessors, and backup info.

## Risks And Edge Cases

- Many wrappers assume non-null input pointers and valid array lengths; only newer compaction-service/open-and-compact functions contain explicit argument checks.
- Callback destructor pointers are often called unconditionally in adapter destructors; null destructors can crash.
- `CopyString` calls `malloc(slice.size())` and then `memcpy`, which may return null for zero-length buffers depending on allocator behavior. Callers must rely on returned lengths rather than C-string termination; `CopyString` does not add a null terminator.
- Some string-returning APIs use `strdup` and are null-terminated, while binary-returning APIs use `malloc`; FFI bindings must not assume one convention.
- Reinterpret casts of RocksDB C++ event info or `rocksdb_slice_t` to wrapper/Slice types rely on exact layout assumptions.
- Metadata child wrappers and iterator slice returns are borrowed views; stale access after parent destruction or movement is unsafe.
- `rocksdb_slicetransform_t::Transform` returns a `Slice` pointing at a callback-returned `char*` without visible ownership/free logic in this chunk, so callback implementations must obey RocksDB expectations to avoid leaks or dangling pointers.
- `rocksdb_create_column_families_destroy` frees only the returned array, not the individual handles, so callers must destroy handles separately.
- `rocksdb_create_column_family_with_ttl` returns a handle even if `CreateColumnFamilyWithTtl` fails, unlike some other create paths that delete the handle on error.
- `rocksdb_compactionservice_t::Wait` casts callback status directly to `CompactionServiceJobStatus` without range validation, unlike scheduler response creation.
- Event listener callbacks are invoked without null checks for individual callback pointers; users must provide all callbacks or risk crashes when events fire.
- `rocksdb_level_metadata_t` and `rocksdb_sst_file_metadata_t` are allocated with `malloc`, not `new`, because they only store borrowed pointers. Destruction must use the matching free path; the chunk ends before the body of `rocksdb_sst_file_metadata_destroy`.

## Test Signals

- Existing C binding tests should exercise open/close, put/get/delete/merge, column families, multiget, iterators, snapshots, write batches, write-batch-with-index, options setters/getters, cache/env creation, backup/restore, checkpoint/export/import, SST writer, external ingestion, and metadata traversal.
- FFI tests should check binary keys/values with embedded null bytes, zero-length values, timestamped APIs, not-found behavior with null error pointers, per-key multiget errors, and consistent freeing of returned buffers.
- Callback tests should cover custom comparator, comparator-with-timestamp, merge operator, compaction filter/factory, prefix extractor, logger, event listener, and compaction service lifecycle/destructor behavior.
- Persistence tests should validate WAL iteration sequence numbers, flush/compaction effects, live-file and column-family metadata accuracy, backup option behavior, checkpoint export/import, and secondary catch-up.
- Stress tests should include invalid enum/status values, null optional bounds/timestamps, large multiget batches, pinned-slice lifetime, base iterator transfer in `WriteBatchWithIndex`, and parent/child metadata destruction order.

### subset-b-008571: lines 7444-8988

# sources/storage-engines/rocksdb/db/c.cc lines 7444-8988

## Scope

This chunk is the tail of RocksDB's C API implementation. It starts in SST file metadata accessors, then covers import/export metadata helpers, almost all TransactionDB and OptimisticTransactionDB C wrappers, generic pinned-read helpers, approximate memory-usage wrappers, a few late option setters, compaction control wrappers, histogram-data accessors, wait-for-compact options, and the newer zero-copy/buffered Get APIs. The file ends by closing `extern "C"`.

The code does not implement storage algorithms directly. It is an ABI bridge: each exported `rocksdb_*` function unwraps an opaque C handle, builds C++ `Slice`, `std::vector`, `ColumnFamilyDescriptor`, or option objects as needed, calls the corresponding RocksDB C++ API, translates `Status` through `SaveError`, and returns C-compatible handles, buffers, or scalar values.

## Purpose

The main purpose of this chunk is to expose RocksDB transactional and diagnostic functionality to C callers while preserving RocksDB C++ ownership and status semantics. It lets C clients:

- inspect SST file metadata and construct import/export metadata objects;
- configure and open `TransactionDB` and `OptimisticTransactionDB` instances;
- begin, reuse, prepare, commit, roll back, name, and destroy transactions;
- read, write, merge, delete, batch-write, iterate, flush, checkpoint, and inspect properties through transaction-aware DB handles;
- use both locking reads (`GetForUpdate`) and optimistic transactions;
- retrieve pinned values or copy values into caller-provided buffers;
- estimate DB/cache memory usage through `MemoryUtil`;
- control background compaction and wait for compaction completion;
- read histogram data fields through the C API.

The wrapper layer keeps source-level compatibility with `include/rocksdb/c.h`: callers only see opaque pointer types and must use the matching create/destroy/free functions.

## Important APIs, Types, And Functions

### Metadata And Import/Export Helpers

- `rocksdb_sst_file_metadata_get_relative_filename()`, `rocksdb_sst_file_metadata_get_directory()`, `rocksdb_sst_file_metadata_get_size()`, `rocksdb_sst_file_metadata_get_smallestkey()`, and `rocksdb_sst_file_metadata_get_largestkey()` expose `SstFileMetaData` fields. Filename/directory strings are `strdup()`-allocated; key buffers are allocated by `CopyString()` and return lengths out-of-band.
- `rocksdb_import_column_family_options_create()`, `rocksdb_import_column_family_options_set_move_files()`, and `rocksdb_import_column_family_options_destroy()` wrap `ImportColumnFamilyOptions`, currently only exposing `move_files`.
- `rocksdb_export_import_files_metadata_create()` allocates a `rocksdb_export_import_files_metadata_t` plus a heap-owned `ExportImportFilesMetaData`. Its comparator-name accessors copy between C strings and `std::string`.
- `rocksdb_export_import_files_metadata_get_files()` returns a new `rocksdb_livefiles_t` containing a copied `std::vector<LiveFileMetaData>`.
- `rocksdb_export_import_files_metadata_set_files()` moves the supplied `rocksdb_livefiles_t::rep` into metadata and deletes the wrapper. That is a transfer-of-ownership API: the caller must not reuse the `rocksdb_livefiles_t*` afterward.
- `rocksdb_export_import_files_metadata_destroy()` deletes both the nested `ExportImportFilesMetaData` and the wrapper.

### Transaction Options And DB Opening

- `rocksdb_transactiondb_options_t` wraps `TransactionDBOptions`. Setters expose `max_num_locks`, `num_stripes`, `transaction_lock_timeout`, `default_lock_timeout`, `write_policy` cast to `TxnDBWritePolicy`, and `use_per_key_point_lock_mgr`.
- `rocksdb_transaction_options_t` wraps `TransactionOptions`. Setters expose snapshot creation, deadlock detection, lock timeout, expiration, deadlock-detection depth, max write-batch size, and `skip_prepare`.
- `rocksdb_optimistictransaction_options_t` wraps `OptimisticTransactionOptions`, currently exposing `set_snapshot`.
- `rocksdb_transactiondb_open()` calls `TransactionDB::Open(options->rep, txn_db_options->rep, name, &txn_db)` and returns a new `rocksdb_transactiondb_t` on success.
- `rocksdb_transactiondb_open_column_families()` builds a `std::vector<ColumnFamilyDescriptor>` from parallel C arrays, opens all requested column families, then wraps each returned `ColumnFamilyHandle*` with `immortal = false`.
- `rocksdb_transactiondb_create_column_family()` wraps `CreateColumnFamily()` and initializes the returned handle only after success.
- `rocksdb_optimistictransactiondb_open()` and `rocksdb_optimistictransactiondb_open_column_families()` mirror the TransactionDB open paths for `OptimisticTransactionDB`.

### Transaction Lifecycle And Two-Phase Commit

- `rocksdb_transaction_begin()` creates a new `rocksdb_transaction_t` when `old_txn == nullptr`; otherwise it passes the old `Transaction*` back to `BeginTransaction()` for reuse and stores the returned pointer into the existing wrapper.
- `rocksdb_optimistictransaction_begin()` has the same reuse behavior for `OptimisticTransactionDB`.
- `rocksdb_transactiondb_get_prepared_transactions()` calls `GetAllPreparedTransactions()`, allocates a C array with `malloc()`, wraps each `Transaction*`, and returns the count. An empty set returns `nullptr` with `*cnt = 0`.
- `rocksdb_transaction_set_name()` and `rocksdb_transaction_get_name()` expose transaction names. The getter returns a `CopyString()` buffer and length.
- `rocksdb_transaction_prepare()`, `rocksdb_transaction_commit()`, `rocksdb_transaction_rollback()`, `rocksdb_transaction_set_savepoint()`, and `rocksdb_transaction_rollback_to_savepoint()` directly delegate to the C++ transaction.
- `rocksdb_transaction_destroy()` deletes both the underlying `Transaction*` and the wrapper.
- `rocksdb_transaction_get_writebatch_wi()` allocates a `rocksdb_writebatch_wi_t` with `malloc()` and points it at `txn->rep->GetWriteBatch()`. It does not create an independent batch; the pointer is tied to the transaction's lifetime.
- `rocksdb_transaction_rebuild_from_writebatch()` and `_wi()` rebuild transaction contents from a plain `WriteBatch` or a `WriteBatchWithIndex`'s internal batch.

### Transactional Reads

- `rocksdb_transaction_get()` and `rocksdb_transaction_get_cf()` read through `Transaction::Get()` into a stack `PinnableSlice`, then copy found values into newly allocated buffers.
- `rocksdb_transaction_get_pinned()` and `_cf()` return a heap `rocksdb_pinnableslice_t` whose embedded `PinnableSlice` owns or pins the value until `rocksdb_pinnableslice_destroy()`.
- `rocksdb_transaction_get_for_update()` and `_cf()` call `Transaction::GetForUpdate()` and therefore acquire transaction locks according to the `exclusive` flag.
- `rocksdb_transaction_get_pinned_for_update()` uses `v->rep.GetSelf()` and `PinSelf()` after `GetForUpdate()`, unlike most other pinned helpers that pass `&v->rep` directly. This makes its self-pinning behavior an important edge case.
- `rocksdb_transaction_get_pinned_for_update_cf()` is the column-family variant using the direct `&v->rep` path.
- `rocksdb_transaction_multi_get()` and `_cf()` convert C arrays into vectors because the transaction API only exposes vector-based `MultiGet`.
- `rocksdb_transaction_multi_get_for_update()` and `_cf()` call `MultiGetForUpdate()` and return per-key values plus per-key error strings. Not-found entries are represented as null values with null errors.

### TransactionDB Reads And Writes Outside A Transaction

- `rocksdb_transactiondb_get()`, `_get_cf()`, `_get_pinned()`, and `_get_pinned_cf()` call `TransactionDB::Get()` against either the default column family or a supplied handle.
- `rocksdb_transactiondb_multi_get()` uses the array-based `DB::MultiGet()` overload with a default-column-family handle and `std::vector<PinnableSlice>` to reduce temporary allocations.
- `rocksdb_transactiondb_multi_get_cf()` builds parallel arrays of `ColumnFamilyHandle*` and `Slice`, then uses the multi-column-family array overload.
- `rocksdb_transactiondb_put()`, `_put_cf()`, `_merge()`, `_merge_cf()`, `_delete()`, and `_delete_cf()` expose non-transactional mutations through the TransactionDB handle.
- `rocksdb_transactiondb_write()` writes a supplied `rocksdb_writebatch_t`.
- `rocksdb_transactiondb_flush_wal()`, `_flush()`, `_flush_cf()`, and `_flush_cfs()` expose WAL and memtable flush operations.

### Transactional Writes, Iterators, Checkpoints, And Base DB Access

- `rocksdb_transaction_put()`, `_put_cf()`, `_merge()`, `_merge_cf()`, `_delete()`, and `_delete_cf()` mutate the transaction's write set rather than the DB directly.
- `rocksdb_transaction_set_commit_timestamp()` and `rocksdb_transaction_set_read_timestamp_for_validation()` expose timestamp hooks used by timestamp-aware transaction modes.
- `rocksdb_transaction_put_log_data()` appends opaque log data to the transaction's write batch for WAL consumers.
- `rocksdb_transaction_create_iterator()` and `_cf()` return iterators created by the transaction, so reads include the transaction's pending writes according to RocksDB transaction semantics.
- `rocksdb_transactiondb_create_iterator()` and `_cf()` create normal DB iterators outside a transaction.
- `rocksdb_transactiondb_checkpoint_object_create()` and `rocksdb_optimistictransactiondb_checkpoint_object_create()` wrap `Checkpoint::Create()`.
- `rocksdb_transactiondb_get_base_db()` and `rocksdb_optimistictransactiondb_get_base_db()` return non-owning `rocksdb_t` wrappers around `GetBaseDB()`. Their close functions delete only the wrapper, not the underlying DB.
- `rocksdb_transactiondb_close()` and `rocksdb_optimistictransactiondb_close()` delete the owning DB object and wrapper.

### OptimisticTransactionDB Helpers

- `rocksdb_optimistictransactiondb_property_value()` and `_property_int()` mirror DB property accessors for `OptimisticTransactionDB`.
- `rocksdb_optimistictransactiondb_write()` exposes a direct write-batch path.
- Optimistic transactions reuse the same `rocksdb_transaction_t` wrapper and transaction read/write functions as locking transactions after `rocksdb_optimistictransaction_begin()` returns a `Transaction*`.

### Generic Pinned Reads And Memory Utilities

- `rocksdb_free()` is the generic deallocator for buffers allocated by `malloc()`, `strdup()`, or `CopyString()`.
- `rocksdb_get_pinned()` and `rocksdb_get_pinned_cf()` expose pinned DB reads outside transactions.
- `rocksdb_pinnableslice_destroy()` deletes a `rocksdb_pinnableslice_t`; `rocksdb_pinnableslice_value()` returns a pointer valid only while that object remains alive.
- `rocksdb_memory_consumers_t` stores DB wrappers and cache wrappers for `MemoryUtil`.
- `rocksdb_memory_consumers_add_db()` records a `rocksdb_t*`; `rocksdb_memory_consumers_add_cache()` stores cache wrappers in an `unordered_set` to deduplicate repeated cache inputs.
- `rocksdb_approximate_memory_usage_create()` unwraps `DB*` and `Cache*`, calls `MemoryUtil::GetApproximateMemoryUsageByType()`, and returns a `rocksdb_memory_usage_t` with memtable total, unflushed memtable, table reader total, and cache total.
- The memory usage getters expose those four counters; `rocksdb_approximate_memory_usage_destroy()` deletes the result object.

### Options, Compaction Controls, Histogram Data, And WaitForCompact

- `rocksdb_options_set_dump_malloc_stats()`, `rocksdb_options_set_memtable_whole_key_filtering()`, `rocksdb_options_set_avoid_unnecessary_blocking_io()`, and `rocksdb_options_get_avoid_unnecessary_blocking_io()` expose late option fields.
- `rocksdb_cancel_all_background_work()`, `rocksdb_disable_manual_compaction()`, `rocksdb_enable_manual_compaction()`, `rocksdb_abort_all_compactions()`, and `rocksdb_resume_all_compactions()` delegate to DB/background-work controls.
- `rocksdb_statistics_histogram_data_create()` value-initializes a `HistogramData` wrapper; the getters expose median, p95, p99, average, standard deviation, max, count, sum, and min.
- `rocksdb_wait_for_compact()` calls `DB::WaitForCompact()`.
- `rocksdb_wait_for_compact_options_create()`, destroy, and field accessors expose `abort_on_pause`, `flush`, `close_db`, and `timeout` as microseconds using `std::chrono::microseconds`.

### New Zero-Copy And Buffer-Oriented Get APIs

- `rocksdb_pinnable_handle_t` is a separate handle type with an embedded `PinnableSlice`.
- `rocksdb_get_pinned_v2()` and `_cf_v2()` allocate a `rocksdb_pinnable_handle_t`, read into `handle->rep`, and return null on not found or error. Non-not-found errors are reported through `SaveError`.
- `rocksdb_pinnable_handle_get_value()` returns a pointer and length into the pinned handle; `rocksdb_pinnable_handle_destroy()` releases it.
- `rocksdb_get_into_buffer()` and `_cf()` perform a Get into a stack `PinnableSlice`, set `*found`, set `*vallen` to the actual value length, copy into the caller buffer only when `buffer_size >= value_size`, and return `1` only when data was copied. A too-small buffer returns `0` but still reports `found = 1` and the required length.

## Control Flow

Most functions have a shallow wrapper flow: construct temporary C++ objects from C inputs, call one C++ method, then translate the result. Error-bearing operations call `SaveError(errptr, status_or_expression)`. If `SaveError()` returns true in open/create functions, the wrapper discards partially allocated C wrappers and returns null.

Open-column-family flow builds descriptors from parallel C arrays before calling the C++ `Open()` overload. On success, RocksDB returns a vector of `ColumnFamilyHandle*`; the wrapper allocates one C handle per returned pointer and stores it into the caller's output array. The C wrapper assumes the caller provided enough output slots for the number of requested column families.

Transaction-begin flow supports allocation and reuse. With no old wrapper, a new C wrapper is allocated and populated with `BeginTransaction(..., nullptr)`. With an old wrapper, its existing `Transaction*` is handed back to RocksDB as the reusable transaction object, and the returned pointer replaces `old_txn->rep`. This avoids wrapper churn but makes correct transaction destruction and no-use-after-destroy important.

Get flow distinguishes not-found from true errors. On `Status::OK`, the wrappers set the output length and either copy bytes or return a pinned wrapper. On `IsNotFound()`, they return null or `success = 0` without setting an error string. On other failures, they return null/zero and populate `errptr`.

MultiGet flow returns a result triple per key. Values are allocated only for successful keys. Missing keys produce `values_list[i] = nullptr`, size zero, and `errs[i] = nullptr`; operational errors produce a null value, size zero, and a `strdup()` status string. Transaction MultiGet paths use vectors because the transaction APIs do not have the same array-based overloads as DB/TransactionDB.

Prepared-transaction recovery flow calls `GetAllPreparedTransactions()` after reopening a TransactionDB, wraps each returned prepared transaction, then expects the caller to inspect names and commit or roll back each wrapper. The array itself is `malloc()`-owned; individual wrappers are destroyed through `rocksdb_transaction_destroy()`.

Memory-usage flow collects handles first, then asks `MemoryUtil` for usage by type. The wrapper maps the resulting `std::map<UsageType, uint64_t>` into a small C struct. Missing map entries default to zero through `operator[]`.

Wait-for-compact flow is option-object based. Callers allocate a `rocksdb_wait_for_compact_options_t`, set booleans and timeout, pass it to `rocksdb_wait_for_compact()`, then destroy it.

## State And Persistence Behavior

The chunk mostly mutates C++ RocksDB state through public APIs rather than editing storage files directly.

Persistent DB state can change through transaction commits, direct TransactionDB writes, OptimisticTransactionDB writes, flushes, WAL flushes, checkpoints, compaction controls, and background-work cancellation. Transactional writes remain in the transaction object until commit. Rollback and rollback-to-savepoint discard transaction-local writes; commit persists them according to RocksDB's write options, write policy, WAL, and column-family configuration.

Two-phase commit state is persistent. `Prepare()` records prepared transactions so `rocksdb_transactiondb_get_prepared_transactions()` can recover them after DB close/reopen. Transaction names are part of the identification path used by C tests to decide which recovered prepared transaction to commit or roll back.

Snapshots returned by `rocksdb_transactiondb_create_snapshot()` point into the DB's snapshot machinery and must be released with `rocksdb_transactiondb_release_snapshot()`. `rocksdb_transaction_get_snapshot()` is unusual: it allocates the C wrapper with `malloc()` and stores the transaction's snapshot pointer; its comment says it will be freed later with `free`, which differs from the DB snapshot wrapper that is deleted in `release_snapshot()`.

Pinned read state is memory-lifetime sensitive. `rocksdb_pinnableslice_value()` and `rocksdb_pinnable_handle_get_value()` expose pointers into a `PinnableSlice`; those pointers are valid only until the corresponding destroy call or until any owning DB/transaction state invalidates the pin according to RocksDB's C++ contract. Copying getters avoid that lifetime constraint by returning caller-freed buffers.

Base DB wrappers returned from transaction DBs are non-owning shells over `GetBaseDB()`. Closing those wrappers only deletes the wrapper, while closing the transaction DB deletes the owning C++ transaction DB object.

Import/export metadata helpers store comparator names and file metadata in heap C++ objects under C wrappers. `set_files()` consumes the provided livefiles wrapper by moving its vector into the metadata object, which changes the caller-visible ownership state immediately.

Memory usage objects are snapshots of approximate usage at call time. They do not update after DB/cache memory changes.

## Dependencies And Integration Points

This chunk depends on wrapper structs defined earlier in the same file: `rocksdb_t`, `rocksdb_options_t`, `rocksdb_readoptions_t`, `rocksdb_writeoptions_t`, `rocksdb_column_family_handle_t`, `rocksdb_writebatch_t`, `rocksdb_writebatch_wi_t`, `rocksdb_snapshot_t`, `rocksdb_checkpoint_t`, `rocksdb_pinnableslice_t`, and the transaction/option/statistics wrapper types.

It integrates with RocksDB C++ APIs and utility types imported near the top of `c.cc`, including:

- `DB`, `TransactionDB`, `OptimisticTransactionDB`, `Transaction`, `TransactionDBOptions`, `TransactionOptions`, `OptimisticTransactionOptions`, and `TxnDBWritePolicy`;
- `ColumnFamilyDescriptor`, `ColumnFamilyOptions`, `ColumnFamilyHandle`, `DBOptions`, `ReadOptions`, `WriteOptions`, `FlushOptions`, and `WaitForCompactOptions`;
- `Slice`, `PinnableSlice`, `Status`, `WriteBatch`, `WriteBatchWithIndex`, `Checkpoint`, `MemoryUtil`, `Cache`, `HistogramData`, `LiveFileMetaData`, `SstFileMetaData`, `ImportColumnFamilyOptions`, and `ExportImportFilesMetaData`;
- local helpers such as `SaveError()` and `CopyString()`.

The public declarations live in `sources/storage-engines/rocksdb/include/rocksdb/c.h`. The behavior is exercised heavily by `sources/storage-engines/rocksdb/db/c_test.c`, especially the `transactions`, `two-phase commit`, `transactions_multi_get_for_update`, `optimistic_transactions`, `zero_copy_get_pinned_v2`, `pin_get`, and `wait_for_compact` phases.

Column-family integration follows the standard C API pattern: handles are not immortal except for the default column family and must be destroyed by callers when no longer needed. TransactionDB and OptimisticTransactionDB column-family opens return handles that refer to the opened DB and must not outlive it.

## Risks And Edge Cases

- Ownership is mixed across `new`, `delete`, `malloc`, `free`, `strdup`, and `CopyString()`. Callers must use the specific destroy/free API expected by each returned object. `rocksdb_transaction_get_writebatch_wi()` in particular uses `malloc()` for a wrapper that points into the transaction.
- `rocksdb_export_import_files_metadata_set_files()` deletes the supplied `rocksdb_livefiles_t*` after moving from it. Reusing or destroying that pointer again would be a use-after-free/double-free bug.
- Base DB wrappers from `rocksdb_transactiondb_get_base_db()` and `rocksdb_optimistictransactiondb_get_base_db()` do not own the underlying `DB*`. Closing the parent transaction DB while a base wrapper is still in use would leave the wrapper dangling.
- Transaction reuse through `rocksdb_transaction_begin(..., old_txn)` assumes the old wrapper is valid and its old `Transaction*` is reusable by RocksDB. Reusing after destroy, or using old transaction state after begin replaces it, is unsafe.
- Prepared transactions returned by `rocksdb_transactiondb_get_prepared_transactions()` are real `Transaction*` objects from RocksDB. Each wrapper must be committed/rolled back or destroyed exactly once, and the returned pointer array must be freed separately.
- MultiGet error arrays mix nulls and allocated error strings. Callers need to free only non-null error strings and returned value buffers.
- Not-found status is intentionally not an error for Get and MultiGet. Tests should verify callers can distinguish not found from I/O/corruption/status failures through null result plus null error.
- `rocksdb_transaction_get_pinned_for_update()` uses `GetSelf()`/`PinSelf()` before checking status. If this path diverges from other pinned helpers, it is a likely area for lifetime or empty-value regressions.
- `rocksdb_transaction_get_snapshot()` uses `malloc()` for a `rocksdb_snapshot_t`, unlike `rocksdb_transactiondb_create_snapshot()` which uses `new` and has an explicit release function. Mixing release paths would corrupt memory.
- `rocksdb_transactiondb_options_set_write_policy()` casts an int to `TxnDBWritePolicy` without validation. Invalid enum values can only be rejected, if at all, by lower RocksDB layers.
- `rocksdb_get_into_buffer()` returns `0` for both not found and buffer-too-small; callers must inspect `found` and `vallen` to distinguish them.
- Pinned value pointers returned by either old `rocksdb_pinnableslice_t` or new `rocksdb_pinnable_handle_t` become invalid after destroy. They should not be cached across handle destruction or DB close.
- Memory consumers store raw wrapper pointers. Destroying a DB or cache before calling `rocksdb_approximate_memory_usage_create()` with the consumer list would make the list invalid.
- `rocksdb_wait_for_compact_options_set_timeout()` accepts a `uint64_t` microsecond count and converts to `std::chrono::microseconds`; extreme values may depend on the representation width of the chrono duration.
- Compaction-control wrappers directly affect background work and manual compaction state on the DB. Tests need to consider races with concurrent flush/compaction and DB close.

## Test Signals

Existing `c_test.c` coverage signals for this chunk include:

- `wait_for_compact`: creates wait-for-compact options, calls `rocksdb_wait_for_compact()`, and destroys the options object.
- `transactiondb_set_write_policy_prepared`: sets `rocksdb_txndb_write_policy_write_prepared`, opens a TransactionDB, writes inside a transaction, commits, and verifies the value.
- `transactions`: covers direct TransactionDB put/delete/write-batch, transaction put/delete/commit/rollback/savepoint, transaction name get/set, snapshots, iterators, column-family operations, base DB access, memory-usage creation, WAL flush, memtable flush, and pinned reads.
- `two-phase commit`: verifies prepare/commit error ordering, transaction naming before prepare, persistence of two prepared transactions across close/reopen, `get_prepared_transactions()`, and separate commit/rollback of recovered transactions.
- `transactions_multi_get_for_update`: verifies `MultiGetForUpdate` locks keys, conflicting `GetForUpdate` reports an error, and the column-family variant has the same lock behavior.
- `optimistic_transactions`: opens an OptimisticTransactionDB, runs multiple optimistic transactions, tests base DB access, column-family transaction writes, pinned transaction reads, MultiGet with column families, and transaction iterators.
- `zero_copy_get_pinned_v2`: verifies `rocksdb_get_pinned_v2()` success and not-found behavior, plus `rocksdb_get_into_buffer()` success, buffer-too-small reporting, and not-found reporting.
- `pin_get`: covers column-family pinned and buffer-oriented Get variants, including too-small-buffer behavior.

Additional useful tests for this chunk would include:

- explicit freeing discipline for every returned string, value buffer, error string, prepared transaction array, pinned slice, and pinned handle under leak sanitizers;
- `rocksdb_export_import_files_metadata_set_files()` ownership transfer and no double-destroy of the moved `rocksdb_livefiles_t`;
- invalid transaction write-policy integer values and invalid transaction timeout/lock settings;
- `rocksdb_transaction_get_pinned_for_update()` lifetime and conflict behavior compared with `_cf` and non-pinned variants;
- `rocksdb_transaction_get_snapshot()` release path coverage to ensure the malloc-allocated wrapper is freed consistently by the public API contract;
- TransactionDB/OptimisticTransactionDB open-column-family error paths with partially invalid descriptors;
- `rocksdb_get_into_buffer()` with zero-length values, zero-size caller buffers, exact-size buffers, and non-not-found errors;
- memory-usage calls with duplicate caches, multiple DBs, no consumers, and destroyed-consumer cleanup;
- compaction pause/abort/resume/wait interactions, including `abort_on_pause`, `flush`, `close_db`, and timeout settings.
