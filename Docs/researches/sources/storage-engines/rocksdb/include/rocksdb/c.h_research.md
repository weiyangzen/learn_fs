# sources/storage-engines/rocksdb/include/rocksdb/c.h

## Purpose

`c.h` is RocksDB's exported C ABI surface. It exposes opaque handles for the C++ database, options, cache, backup, transaction, compaction, iterator, snapshot, memory, and remote-compaction objects, plus C-callable constructors, destructors, mutators, and operation functions. The header is intentionally broad: it allows non-C++ callers such as JNI, FFI bindings, and shared-library consumers to drive RocksDB without depending on C++ type layout or name mangling. It also states the central C API conventions: all implementation types are opaque pointers; slices are modeled as pointer-plus-length; most fallible calls use `char** errptr`; booleans are `unsigned char`; and pointer arguments are expected non-null.

## Important APIs, Types, and Functions

The file defines `ROCKSDB_LIBRARY_API` for Windows DLL import/export and wraps declarations in `extern "C"`. It forwards dozens of opaque structs, including `rocksdb_t`, `rocksdb_options_t`, `rocksdb_column_family_handle_t`, `rocksdb_iterator_t`, `rocksdb_writebatch_t`, `rocksdb_cache_t`, transaction DB handles, backup handles, and remote compaction handles. `rocksdb_slice_t` is the one exposed value struct, ABI-shaped for zero-copy slice interop with `{const char* data; size_t size;}`.

Core DB lifecycle functions include `rocksdb_open`, TTL/read-only/secondary open variants, column-family open variants, `rocksdb_close`, `rocksdb_destroy_db`, and `rocksdb_repair_db`. Data operations cover put/delete/single-delete/delete-range/merge/write-batch, timestamp variants, multi-get, batched multi-get, `key_may_exist`, pinned get, zero-copy pinned handle APIs, and direct `rocksdb_get_into_buffer`. Read surfaces include iterators, WAL iterators, snapshots, properties, approximate sizes, live-file metadata, metadata trees, and memory-usage accounting.

The options surface is extensive. It includes create/copy/destroy, dynamic `rocksdb_set_options`, DB/CF option setters and getters, table options, compression and blob settings, rate limiters, write/read/compact/flush options, compaction styles, FIFO/universal options, WAL recovery and compression enums, statistics/perf context, Env and EnvOptions, SST file writer and external-file ingest, write buffer manager, SST file manager, cache and allocator configuration, event listeners, compaction filters/factories, comparators including timestamp-aware comparators, filter policies, merge operators, slice transforms, backup/restore, checkpoint/export/import, and transaction/optimistic transaction APIs.

Remote compaction support is represented by callback typedefs for scheduling, waiting, cancellation, and installation notification; `rocksdb_compactionservice_t`; job status enums; scheduler response and job-info accessors; compaction-service option overrides; cancellation flag helpers; and `rocksdb_open_and_compact` entry points.

## Control Flow

This header declares, rather than implements, control flow. The visible flow contract is handle-oriented: callers create option/configuration objects, pass them into open or factory functions, perform DB operations with read/write/compact/flush options, inspect output handles or buffers, then release resources with the matching destroy/close/free functions. Error flow is out-of-band through `char** errptr`: successful calls leave existing error storage unchanged, while failures free any previous error string and replace it with a malloc-owned message.

Several APIs encode callback flow. User-provided C callbacks drive compaction filters, compaction filter factories, comparators, merge operators, slice transforms, loggers, event listeners, and remote compaction services. For event listeners, RocksDB invokes callback pointers on flush/compaction/subcompaction/external-file-ingestion/background-error/stall/memtable events. For remote compaction, RocksDB asks the service to schedule work, waits for job output, cancels queued jobs, and reports installation status.

## State and Persistence Behavior

The API gives callers control over persistent RocksDB state: DB directories, WAL directories, column-family metadata, manifest identity flags, WAL tracking, backups, checkpoints, SST file ingestion, export/import metadata, TTL, user-defined timestamps, blob files, compaction output, and transactions. It also exposes operational state such as snapshots, iterators, pinned values, live files, cache usage, perf context counters, statistics histograms, memory-usage approximations, file deletion disable/enable state, manual compaction enable/disable state, and background work cancellation.

Ownership is a major part of the state contract. Returned malloc-owned strings and buffers must be released with `rocksdb_free` unless a more specific destroy function is documented. Handles created by `*_create` generally require matching `*_destroy`; DB-like handles require close functions; snapshot handles must be released against the owning DB; iterator and pinnable handles pin resources until destroyed. Some comments call out special cases, for example backup stop is one-way for a backup engine, transaction snapshot/write-batch handles have specific free/destroy expectations, and `rocksdb_cache_disown_data` intentionally changes cache ownership behavior.

## Dependencies and Integration Points

`c.h` depends only on C standard headers plus the RocksDB shared-library ABI macro, but each declaration maps to C++ implementations in `db/c.cc` and RocksDB internals. It integrates with the C++ APIs behind `rocksdb/options.h`, `rocksdb/cache.h`, `rocksdb/comparator.h`, `rocksdb/compaction_filter.h`, transaction DB, backup engine, Env, table factories, PerfContext, and compaction-service code. Search signals show `db/c.cc` implements newer surfaces such as `rocksdb_comparator_with_ts_create`, remote compaction options, and `rocksdb_open_and_compact`; `examples/c_simple_example.c` exercises the basic C lifecycle.

The file is also a binding contract. JNI, language wrappers, and external projects rely on symbol names, argument order, enum values, and ownership semantics staying stable. The timestamp-aware comparator and high-performance get APIs are particularly important integration points for newer UDT and zero-copy binding work.

## Risks and Edge Cases

The dominant risks are ABI and ownership errors. Changing opaque type names, exported symbol signatures, enum values, or error conventions can break downstream FFI consumers. Returning memory from different allocators or failing to document the correct destroy/free function can cause leaks or crashes. `char** errptr` requires callers to initialize and retain ownership correctly; multi-get uses per-key error arrays, which is a different error shape from most calls.

Callback APIs are high risk because RocksDB calls into user code from internal threads. Exceptions are not visible in C, but callback implementers can still crash, leak, or violate comparator/filter invariants. Timestamp APIs require consistent timestamp sizes and comparator semantics. `singledelete`, range deletion, compaction filters, ingest-behind, transaction APIs, and remote compaction all expose behaviors that can affect correctness or persistence if used with incompatible options. The header's "all pointers non-null" convention means callers cannot rely on defensive null checks.

## Test Signals

Useful signals include `examples/c_simple_example.c` for basic C API open/write/read/backup flow, `db/c.cc` for wrapper implementation, Java JNI sources for binding expectations, and RocksDB tests for the underlying C++ features. Search references show timestamp comparator tests in `db/db_with_timestamp_*`, `utilities/transactions/write_committed_transaction_ts_test.cc`, comparator implementation tests, cache tests, compaction filter blob tests, and cleanable/cache tests that indirectly validate handles and pinned-resource lifetimes exposed by the C API.
