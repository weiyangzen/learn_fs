# sources/storage-engines/rocksdb/db/db_iter.h

## Purpose

`db_iter.h` declares and largely defines the public/private shape of `DBIter`, RocksDB's adapter from an `InternalIterator` over `(user key, sequence, value type)` records to the public `Iterator` interface over visible user entries. The header documents the iterator's core contract: at a given sequence number, expose the newest live value for each user key while accounting for tombstones, merges, blob indexes, wide columns, timestamps, bounds, and prefix scan constraints.

## Important APIs, types, and members

`DBIter::NewIter()` is the allocation/factory entry point. It accepts environment, read options, immutable and mutable CF options, comparator, wrapped internal iterator, version, sequence, optional read callback, active memtable, optional column-family handle, blob-index exposure flag, optional arena, and optional DB/CF data. It can allocate from an arena and derives `DBImpl`/`ColumnFamilyData` from `ColumnFamilyHandleImpl` when provided.

Public `Iterator` methods include `Valid`, `key`, `value`, `columns`, `status`, `timestamp`, `GetProperty`, `Next`, `Prev`, `Seek`, `SeekForPrev`, `SeekToFirst`, `SeekToLast`, `PrepareValue`, and `Prepare`. `set_sequence`, `set_valid`, and `set_status` are testing/internal adjustment hooks.

`Direction` captures the positioning invariant: forward mode usually points at the current entry or just after merge contributors, while reverse mode positions the internal iterator before all entries for the exposed key.

`LocalStatistics` batches iterator tickers locally and flushes them in the destructor to avoid per-step atomic-counter overhead.

`BlobReader`/`BlobState` centralize blob value retrieval, lazy blob-index exposure, and direct-write fallback through a blob file cache. `ValueColumnsState` owns the default value slice, materialized wide columns, saved serialized value buffer, lazy entity column vectors, lazy blob-column indexes, resolver, and mutex used to materialize V2 wide-column entities with blob columns.

Private helpers declare all major state-machine operations: direction transitions, seek target encoding, forward/reverse user-entry discovery, merge resolution, visibility checks, value/blob/entity population, tombstone-run tracking, prefix checks, scan preparation, and memtable flush marking.

## Control flow encoded by the declarations

The header separates public movement from internal state machines. Public movement methods reset per-operation state and call helpers. `FindNextUserEntry` drives forward scans. `PrevInternal`, `FindValueForCurrentKey`, and `FindUserKeyBeforeSavedKey` drive reverse scans. `ReverseToForward` and `ReverseToBackward` repair underlying iterator position when callers switch directions.

Value exposure is layered. Plain values set both the default value and a single default wide column. Blob indexes either become the exposed value for legacy BlobDB, stay lazy when `allow_unprepared_value` is true, or are fetched immediately. Wide-column entities deserialize into materialized columns or lazy entity metadata and then resolve blob columns before a valid iterator position is published. Merge helpers normalize no-base, plain-base, blob-base, and wide-column-base cases into a final value or wide-column entity.

## State and persistence behavior

The header makes clear that `DBIter` is mostly transient read state, but it can feed back into mutable DB state. `active_mem_`, memtable sequence lower bound, per-op and average scan-flush triggers, contiguous tombstone counters, range tombstone keys, and ingest-SST lock support read-path flush marking and logically redundant range tombstone insertion. The destructor releases pinned data, deletes the wrapped iterator according to arena mode, records deleted-iterator ticks, resets skipped-key accounting, and flushes local statistics.

Pinning state is explicit. `TempPinData`, `ReleaseTempPinnedData`, `pin_thru_lifetime_`, and `PinnedIteratorsManager` allow short-lived or iterator-lifetime block pinning depending on read options. `DirtyTracked<BlobState>` and `DirtyTracked<ValueColumnsState>` track whether cleanup or reset-sensitive nested state has been mutated.

Timestamp state is also explicit: upper and lower timestamp pointers, timestamp size, saved reverse timestamp, and comparison helpers determine whether keys are compared with or without timestamps. When a lower timestamp bound is active, skip comparisons preserve timestamp distinctions so multiple versions of a user key can be returned.

## Dependencies and integration points

The header includes RocksDB DB, iterator, wide-column, blob, arena, CF options, DB implementation, table iterator wrapper, and dirty-tracking dependencies. It forward-declares `BlobFileCache`, `Version`, and `port::RWMutex`. It is included by `db_iter.cc` and by tests such as `db_iter_stress_test.cc`, and it is part of the DB read path construction pipeline.

`DBIter` sits between storage-specific internal iterators and the public `rocksdb::Iterator` API. It integrates with column families, snapshots/read callbacks, user comparators, prefix extractors, merge operators, blob storage, wide columns, DB tracing, statistics, and active memtable maintenance.

## Risks and edge cases

Because many methods expose slices into saved buffers, pinned blocks, or deserialized entity vectors, lifetime and reset order are critical. Reverse iteration is only supported when underlying values can be pinned for the cases that need to carry a value while moving the internal iterator. The arena allocation path requires destructor behavior to delete the wrapped iterator without assuming ordinary heap ownership of `DBIter` itself. Prefix and timestamp modes alter both correctness and optimization eligibility; enabling range tombstone conversion when scans are incomplete would risk hiding live keys. Multi-scan preparation stores scan options and requires later seeks to match the prepared ranges exactly.

## Test signals

The header's contracts are exercised by the implementation and by stress tests that call `DBIter::NewIter` directly. Useful test signals include direction switching, key/value pinning, merge results, status propagation, timestamp range iteration, prefix bounds, lazy blob value preparation through `PrepareValue`, wide-column materialization through `columns`, and local-to-global statistic flushing on destruction.
