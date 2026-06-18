# sources/storage-engines/tikv/components/cdc/src/initializer.rs

## Purpose

`initializer.rs` runs the asynchronous initialization for a newly registered downstream. Its responsibilities are to capture raftstore change observation, establish the ordering barrier between already-observed delta changes and snapshot scan output, optionally build the shared lock resolver, scan incremental changes since the checkpoint, stream scan events to the sink under rate limits, and schedule deregistration on failure.

This file is the bridge from a client registration to a normal CDC stream.

## Important APIs, Types, And Functions

- `ScanStat` records emitted bytes, optional disk-read bytes, and RocksDB perf delta for incremental scan observability.
- `KvEntry` wraps either transactional `TxnEntry` or RawKV `KvPair` so delegate conversion can handle both APIs.
- `Scanner<S>` is either a TxnKV `DeltaScanner<S>` or RawKV `RawMvccIterator`.
- `Initializer<E>` stores all registration identity, checkpoint and epoch, resolver-building flag, observed range, observe handle, downstream state/cancellation, optional tablet, scheduler, sink, scan semaphore/limiters, batch sizing, timestamp-filter ratio, requested KV API, and loop filtering.
- `initialize` acquires the scan concurrency permit, sends `capture_change` to raftstore, schedules `Task::InitDownstream` from the read callback, waits for a pre-scan barrier, and handles the capture-change snapshot response.
- `on_change_cmd_response` either starts `async_incremental_scan` with the snapshot and region or converts a response header error.
- `async_incremental_scan` computes the effective scan range, builds resolver locks when requested, constructs TxnKV or RawKV scanner, loops over `scan_batch`, streams events with `sink_scan_events`, and transitions downstream to `Normal`.
- `do_scan` is the synchronous scan core. It reads up to byte/count batch limits, resolves old values when the ts-filter path emits `OldValue::SeekWrite`, gathers IO/perf stats, and appends `None` as an end marker.
- `scan_batch` updates cumulative stats, flushes RocksDB perf metrics, and applies disk-read and emitted-byte rate limiters.
- `sink_scan_events` converts entries through `Delegate::convert_to_grpc_events`, sends them with cancellation awareness, and waits on a final barrier before allowing resolved-ts.
- `finish_scan_locks` schedules `Task::FinishScanLocks` with the scanned lock map.
- `deregister_downstream` chooses between whole-delegate and single-downstream deregistration based on resolver-building and region-error classification.
- `ts_filter_is_helpful` inspects write-CF table properties, especially max timestamp, to decide whether `DeltaScanner::hint_min_ts` will avoid enough old versions.

## Control Flow

`initialize` first checks whether the downstream was already stopped, then requests raftstore to capture changes for the region using `ChangeObserver::from_cdc`. The raftstore read callback schedules `Task::InitDownstream`, which is handled by endpoint on the serial CDC worker. That endpoint task initializes the delegate lock tracker if needed, sets `build_resolver`, force-sends an incremental-scan barrier to the sink, transitions downstream state from `Uninitialized` to `Initializing`, and finally invokes the paired callback so `initialize` can continue.

The initializer waits for the barrier to complete before reading the capture-change snapshot response. This guarantees delta changes observed before the snapshot are delivered before scan results. If the snapshot exists, `async_incremental_scan` runs.

`async_incremental_scan` first updates `ObservedRange` against the actual region and computes intersection bounds for backwards-compatible clients that did not supply a range. If this initializer is responsible for resolver construction, it scans all storage locks for the whole region, filters to Put/Delete locks, and schedules `FinishScanLocks`.

For TxnKV, the scanner is a `DeltaScanner` over `(checkpoint_ts, max]`, optionally using `hint_min_ts` and `OldValueCursors` when table-property analysis says the timestamp filter is helpful. For RawKV, it creates a RawMVCC iterator over the API v2 raw key prefix and emits versions newer than `checkpoint_ts`.

The loop cancels quickly if downstream state becomes `Stopped`, warns/metrics long scans after 60 seconds, scans a bounded batch, detects completion by a trailing `None`, converts and sends events, and repeats. On completion it atomically moves state from `Initializing` to `Normal`, records scan duration/sink duration, and returns stats.

Errors from initialization call `deregister_downstream`: if resolver construction failed or the error is region-scoped, the whole delegate is deregistered; otherwise only this downstream is removed.

## State And Persistence Behavior

The initializer is transient and owns no durable state. It holds snapshots/iterators while scanning and uses in-memory semaphores/rate limiters/backpressure. Its observable side effects are:

- Scheduling endpoint tasks (`InitDownstream`, `FinishScanLocks`, `Deregister`).
- Sending scan events and barriers into the CDC sink.
- Moving downstream state from `Uninitialized` to `Initializing` to `Normal`, or respecting `Stopped`.
- Setting `scan_truncated` indirectly through sink error paths and responding to it in `send_all`.
- Updating CDC scan, old-value, disk-read, and RocksDB perf metrics.

The scan uses TiKV snapshot contents as the persistent source of truth; no CDC initialization checkpoint is written.

## Dependencies And Integration Points

- `raftstore::router::CdcHandle` and `ChangeObserver` for capture-change read callbacks.
- `endpoint::Task` and `Deregister` for scheduling endpoint state transitions.
- `delegate::{Delegate, MiniLock, ObservedRange, post_init_downstream}` for event conversion, resolver locks, and state transition.
- TiKV MVCC scanners: `DeltaScanner`, `MvccReader`, `ScannerBuilder`, `TxnEntryScanner`, RawKV `RawMvccSnapshot`.
- Rocks engine/table properties and perf context for timestamp-filter decisions and metrics.
- `old_value::{OldValueCursors, near_seek_old_value}` for materializing old values when filter optimization skips old write records.
- `tokio::sync::Semaphore` and `tikv_util::time::Limiter` for concurrency and speed limiting.
- `ApiV2`, engine-traits CF/range APIs, region metadata, fail points, and CDC metrics.

## Risks And Edge Cases

- Correctness depends on the capture-change callback, sink barrier, and snapshot scan ordering. If the barrier is skipped or not force-sent, clients can see scan rows before earlier delta changes.
- Resolver construction scans the whole region, not just the observed subrange, because it is shared across downstreams. This is intentional but increases memory and scan cost.
- `scan_locks_from_storage(None, None, ...)` relies on the region snapshot scope; if snapshot scoping changes, resolver lock coverage could become too broad.
- RawKV scanner iterates the whole RawKV prefix and filters by checkpoint timestamp, while range filtering happens later in event conversion/observed range handling. This can be expensive for small observed ranges.
- `ts_filter_is_helpful` depends on RocksDB table properties and `PROP_MAX_TS`; missing or inaccurate properties disable or misguide the optimization.
- Old-value resolution with `OldValue::SeekWrite` is correctness-sensitive. The missing-range cache test indicates prior risk around cursor movement and repeated misses.
- Long-running scans hold snapshots; scan concurrency and speed limiters mitigate but do not eliminate storage pressure.
- Many storage decoding paths still unwrap parser results from trusted on-disk encodings.

## Test Signals

Initializer tests cover lock scanning and resolver scheduling, observed-range scan filtering, cancellation and sink disconnect failures, transaction source filtering for CDC loop/import/lossy-DDL writes, old-value correctness with `hint_min_ts`, old-value missing-range cache behavior, deregistration policy, semaphore blocking in `initialize`, RawKV and TiDB initialize paths, Titan-backed scanner behavior, and table-property scan-range optimization. The tests are broad for scan correctness and cancellation; full production coverage still depends on endpoint/raftstore integration tests for ordering and leadership changes.
