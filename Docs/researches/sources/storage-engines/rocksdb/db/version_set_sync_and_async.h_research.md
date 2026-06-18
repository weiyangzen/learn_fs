# sources/storage-engines/rocksdb/db/version_set_sync_and_async.h

## Purpose

`version_set_sync_and_async.h` defines the sync/async implementation body for `Version::MultiGetFromSST`, the helper that looks up a batch of keys in one SST file during `Version::MultiGet`. It is included through RocksDB's coroutine compatibility machinery so the same logic can be compiled as a synchronous function or coroutine-backed asynchronous function.

The file is narrowly focused but performance-critical: it bridges version-level multiget batching, table-cache SST reads, per-level performance accounting, blob-index deferral, range-tombstone early stopping, and value-size soft-limit enforcement.

## Important APIs, Types, and Functions

The only defined function is:

`DEFINE_SYNC_AND_ASYNC(Status, Version::MultiGetFromSST)(const ReadOptions& read_options, MultiGetRange file_range, int hit_file_level, bool skip_filters, bool skip_range_deletions, FdWithKeyRange* f, std::unordered_map<uint64_t, BlobReadContexts>& blob_ctxs, TableCache::TypedHandle* table_handle, uint64_t& num_filter_read, uint64_t& num_index_read, uint64_t& num_sst_read)`.

Important inputs and collaborators are:

- `MultiGetRange`, an iterator range over `KeyContext` entries being searched in this SST.
- `FdWithKeyRange* f`, whose `file_metadata` identifies the target SST.
- `TableCache::MultiGet`, called through `CO_AWAIT(table_cache_->MultiGet)` to perform the SST lookup.
- `BlobReadContexts`, grouped by blob file number, used to defer blob value retrieval after blob indexes are decoded.
- `GetContext`, which carries table lookup state, sampled-read flags, returned value/columns, range tombstone coverage, and per-context read counters.
- `ReadOptions::value_size_soft_limit`, used as a batch abort threshold after accumulating returned non-blob value sizes.
- Perf/statistics hooks such as `StopWatchNano`, `PERF_COUNTER_BY_LEVEL_ADD`, `RecordTick`, `RecordInHistogram`, `GET_HIT_L0`, `GET_HIT_L1`, `GET_HIT_L2_AND_UP`, and `SST_BATCH_SIZE`.
- `TEST_SYNC_POINT_CALLBACK("Version::MultiGet::TamperWithBlobIndex", &(*iter))`, which allows tests to corrupt or alter blob-index handling.

The function is compiled only under the sync/async wrapper condition:
`defined(WITHOUT_COROUTINES) || (defined(USE_COROUTINES) && defined(WITH_COROUTINES))`.

## Control Flow and State Behavior

The function first enables a per-level timer when the RocksDB perf level includes non-mutex timing and per-level perf context is active. It then calls `table_cache_->MultiGet()` with the internal comparator, target file metadata, mutable CF options, the file-read histogram for `hit_file_level`, filter/range-deletion skip flags, and an optional table handle.

If the table-cache lookup returns a non-OK status, the function assigns that status to every key in `file_range`, marks each key done, and returns immediately. This treats SST-level read failure as applying to all keys in the file batch.

For each key context after a successful table-cache call, the function gives the existing `KeyContext` status priority over `GetContext` state. Non-OK per-key statuses are marked done and skipped. For OK statuses, sampled reads update file-read sampling counters, including collapsible-entry sampling when the state is not found, merge, or deleted.

The function accumulates index/filter/SST read counters from each `GetContext`, adds them to the caller-provided per-file/per-level totals, and resets the per-key counters so later levels do not double count them. It reports `GetContext` counters immediately for found/non-merge results when DB statistics are enabled.

Range tombstone coverage affects the search. If a key remains not-found or merge and `max_covering_tombstone_seq > 0`, the remaining files can only contain covered versions for that key, so the key is skipped from further file searches.

The main state machine branches on `GetContext::State()`:

- `kNotFound` keeps the key in the search.
- `kMerge` keeps searching so operands can be resolved or merged by higher-level logic.
- `kFound` records per-level hit statistics, marks the key done, and either decodes a `BlobIndex` into `blob_ctxs` or accumulates value/column serialized size. If accumulated returned value size exceeds `value_size_soft_limit`, the function returns `Status::Aborted()`.
- `kDeleted` converts the status to `NotFound`, marks done, and stops searching the key.
- `kCorrupt` converts the status to corruption for the user key and marks done.
- `kUnexpectedBlobIndex` logs an error, returns a `NotSupported` status explaining BlobDB expectations, and marks done.
- `kMergeOperatorFailed` converts the status to corruption with the merge-operator-failed subcode and marks done.

At the end, it records the observed SST batch size in `SST_BATCH_SIZE` and returns the final status, which is usually OK unless the value-size soft limit aborted the batch.

## State and Persistence Behavior

This helper does not mutate persistent metadata or install versions. Its state changes are per-read and in-memory:

- `file_range` is updated to mark keys done, skipped, or still pending.
- Per-key `Status` objects are filled for errors, deletes, corrupt keys, unexpected blob indexes, or table-read failures.
- `GetContext` read counters are drained into `num_filter_read`, `num_index_read`, and `num_sst_read`.
- Sample-read counters on `FileMetaData` are incremented through `sample_file_read_inc()` and `sample_collapsible_entry_file_read_inc()`.
- Blob-index results are grouped into `blob_ctxs` for later `MultiGetBlob()` resolution rather than reading blobs inline.
- Statistics, histograms, and perf counters are updated for observability.

The persistent SST and blob files are read-only participants. Blob file contents are not fetched here; only encoded blob references are decoded and validated enough to schedule later blob reads.

## Dependencies and Integration Points

The implementation depends on `util/coro_utils.h` for `DEFINE_SYNC_AND_ASYNC`, `CO_AWAIT`, and `CO_RETURN`. It is paired with the `DECLARE_SYNC_AND_ASYNC` declaration in `version_set.h`, and coroutine builds can use it from the async multiget path while non-coroutine builds get equivalent synchronous behavior.

Primary integration points are:

- `Version::MultiGet` and `Version::MultiGetAsync`, which partition user keys by candidate SST/level and call this helper.
- `TableCache::MultiGet`, which performs the actual table-reader lookup.
- `GetContext` and `KeyContext`, which encode per-key result state, values/wide columns, merge/delete/corruption/blob flags, tombstone coverage, and statistics.
- Blob read flow through `BlobIndex`, `BlobReadContexts`, and later `MultiGetBlob()`.
- Perf and statistics subsystems for per-level table-read latency, user-key return counts, L0/L1/L2+ hit ticks, and batch-size histograms.
- SyncPoint-based tests that tamper with blob indexes.

## Risks and Edge Cases

The function relies on the invariant that per-key `Status` is not `NotFound()` after the table-cache call; not-found is represented by `GetContext::kNotFound`. Violating that split would break status precedence and search continuation.

Value-size soft-limit behavior aborts the whole file-range processing once accumulated non-blob result size crosses the threshold. Callers must treat `Status::Aborted()` as a soft-limit signal rather than an SST corruption signal.

Blob-index decoding has two paths: normal values and wide-column default-column values. Missing or malformed data changes the per-key status but does not necessarily fail the entire batch. Unexpected blob indexes are treated as unsupported for non-BlobDB usage and logged.

Range-tombstone skipping depends on `max_covering_tombstone_seq` being set correctly by earlier range-deletion processing. If it is stale or missing, multiget can either waste work searching covered keys or incorrectly stop before a visible older value.

The function resets per-key read counters after adding them to aggregate totals. If a future change forgets the reset, per-level stats can be double counted across levels; if it resets too early, observability loses IO accounting.

Because the file is compiled through sync/async macros, signature drift between `DECLARE_SYNC_AND_ASYNC` in `version_set.h` and this definition will break both build modes. Changes must also preserve coroutine-safe lifetime assumptions for `file_range`, `blob_ctxs`, and table handles.

## Test Signals

Strong test signals include multiget tests covering:

- Correct point lookup across L0/L1/L2+ files with expected per-level hit counters.
- Table-cache read errors propagating to all keys in the affected SST batch.
- Mixed batches where some keys are found, deleted, merged, corrupt, not found, skipped by tombstones, or represented by blob indexes.
- Wide-column values and blob indexes stored in the default wide column.
- `value_size_soft_limit` returning `Status::Aborted()` after enough value bytes are accumulated.
- Blob index tampering via `Version::MultiGet::TamperWithBlobIndex`.
- Per-level perf/stat counters and `SST_BATCH_SIZE` histograms remaining sane after multiple files and levels.
- Async-IO builds producing the same statuses and values as synchronous multiget builds.
