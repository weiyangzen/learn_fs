# sources/storage-engines/tikv/components/backup-stream/src/event_loader.rs

## Purpose
`event_loader.rs` performs initial scanning for a newly observed region. It captures a consistent snapshot from raftstore/CDC, scans MVCC deltas from the region start checkpoint to infinity, converts them to `ApplyEvents`, tracks in-flight locks in the region resolver, and asynchronously sends batches to the backup stream router under memory, throughput, and concurrency limits.

## Important APIs, types, and functions
- `EventLoader<S: Snapshot>` wraps a `DeltaScanner`, region metadata, and a fixed-size `TxnEntry` buffer.
- `EventLoader::load_from` builds a delta scanner over the region key range with `hint_min_ts(from_ts)` and `fill_cache(false)`.
- `fill_entries` reads up to `ENTRY_BATCH_SIZE` entries and stops early when memory quota allocation fails or quota usage exceeds `SLOW_DOWN_INITIAL_SCAN_RATIO`.
- `emit_entries_to` converts `TxnEntry::Prewrite` and `TxnEntry::Commit` into `ApplyEvent`s and tracks eligible prewrite locks in `TwoPhaseResolver`.
- `InitialDataLoader<E, H>` owns the router sink, subscription tracer, scheduler, memory quota, rate limiter, CDC handle, and initial-scan semaphore.
- `capture_change`, `observe_over_with_retry`, `scan_and_async_send`, and `do_initial_scan` are the main initial scan pipeline.

## Control flow
`observe_over_with_retry` repeatedly calls `capture_change`, which registers a `ChangeObserver` through `CdcHandle::capture_change` and waits for a raftstore snapshot callback. Non-retryable region errors such as epoch-not-match, not-leader, stale observe id, and region-not-found stop retrying. After a snapshot is acquired, `do_initial_scan` takes a semaphore permit, constructs an `EventLoader`, and calls `scan_and_async_send`.

`scan_and_async_send` loops: it fills entries while measuring disk-read throughput, validates and mutates the current resolver through `with_resolver`, emits events, consumes rate-limit budget, increments metrics, and spawns an async router send that releases memory when complete. If scanning had to stop because of memory pressure, it joins outstanding send tasks before continuing.

## State and persistence behavior
No durable metadata is written here. Runtime state includes scanner position, buffered entries, memory allocations, joined router-send tasks, resolver lock state, and metrics. Persisted backup data is indirectly produced when `Router::on_events` stores events in temp files or downstream storage.

## Dependencies and integration points
This file bridges raftstore CDC capture, TiKV MVCC scanners, `SubscriptionTracer`/`TwoPhaseResolver`, backup stream `Router`, `Task` scheduler, memory quota, throughput limiter, and metrics. It is constructed by `Endpoint::new` and driven by `RegionSubscriptionManager`.

## Risks and edge cases
- The scan intentionally goes to `TimeStamp::max`, relying on downstream filtering and resolver state.
- Long scans can hold iterators; the semaphore and memory-pressure joins mitigate memtable and memory pressure.
- Resolver lookup also checks region epoch and observe handle id; stale scans are converted to `ObserveCanceled`.
- Shared locks are logged but not tracked, while ordinary locks can fail with `OutOfQuota`.

## Test signals
`test_disk_read` builds a test engine, writes committed data, compacts RocksDB, scans from zero to max, emits events, verifies nonzero events, and verifies measured disk reads are nonzero.
