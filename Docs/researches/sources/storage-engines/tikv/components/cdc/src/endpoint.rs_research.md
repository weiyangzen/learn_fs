# sources/storage-engines/tikv/components/cdc/src/endpoint.rs

## Purpose

`endpoint.rs` implements the central CDC worker endpoint. It owns all active CDC connections, per-region delegates, observer subscriptions, incremental scan runtimes, resolved-ts scheduling, configuration hot updates, old-value cache ingestion, and periodic metrics. It is the event-loop side of the CDC subsystem: service/observer code schedules `Task` values, and `Endpoint` serializes state transitions for registrations, deregistrations, raft batches, scan completion, resolved-ts ticks, and validation callbacks.

## Important APIs, Types, And Functions

- `Deregister` describes all teardown scopes: whole connection, request, region subscription, downstream identity, or whole delegate/observe ID. It carries enough IDs to avoid stale deregistration.
- `Validate` exposes test/diagnostic callbacks over a region delegate, old-value cache, or unresolved region count.
- `Task` is the endpoint message protocol. Key variants are `Register`, `Deregister`, `OpenConn`, `SetConnVersion`, `MultiBatch`, `MinTs`, `FinishScanLocks`, `RegisterMinTsEvent`, `InitDownstream`, `TxnExtra`, `Validate`, and `ChangeConfig`.
- `ResolvedRegion` and `ResolvedRegionHeap` implement a min-heap using `BinaryHeap<Reverse<_>>`; `pop(count)` returns the lowest resolved-ts among popped outlier regions plus their IDs.
- `Advance` accumulates resolved-ts emissions in three protocol shapes: multiplexing by `(ConnId, RequestId)`, exclusive batching by `ConnId`, and legacy compatibility by `(ConnId, region_id)`. `emit_resolved_ts` sends `CdcEvent::ResolvedTs` or legacy `Event_oneof_event::ResolvedTs`.
- `Endpoint<T,E,S>` contains cluster identity, `capture_regions`, `connections`, scheduler, raft CDC handle, local tablets, observer, PD client, timers/runtimes, store meta, concurrency manager, config, scan limiters, sink memory quota, old-value cache, causal-ts provider, and metrics state.
- `Endpoint::new` constructs worker runtimes, speed limiters, old-value cache, leader resolver, initial metrics, and immediately registers the first min-ts event.
- `on_change_cfg` validates and applies online CDC config changes, resizing cache/quota/semaphore and updating scan/fetch speed limiters.
- `on_register` validates a client request, creates/subscribes delegates, installs raftstore observers, builds an `Initializer`, and spawns asynchronous incremental scan.
- `on_deregister`, `deregister_downstream`, and `deregister_observe` own all cleanup.
- `on_multi_batch` routes observed raftstore batches to delegates and schedules delegate teardown on error.
- `finish_scan_locks` reconciles initializer lock-scan output with the current delegate and deregisters failed downstreams.
- `on_min_ts` asks delegates to advance resolved-ts and emits the batched results.
- `register_min_ts_event` schedules asynchronous TSO/causal-ts acquisition and leadership resolution, then reschedules itself.
- `Runnable::run` is the worker dispatch loop; `RunnableWithTimer` flushes metrics every second.
- `CdcTxnExtraScheduler` accepts transaction-extra old-value payloads from the transaction layer, charges memory quota, and schedules `Task::TxnExtra`.

## Control Flow

Connections are opened with `Task::OpenConn`, then version/features are set with `Task::SetConnVersion`. A `Register` request first checks that the connection still exists. If the connection advertises cluster-ID validation, the request header must match `cluster_id`. The requested CDC KV API must be compatible with the store API version. The endpoint also enforces `incremental_scan_concurrency_limit`, returning `server_is_busy` before creating more pending scans.

After validation, `on_register` looks up the local region reader to obtain `txn_extra_op`, records the downstream in the connection, rejects duplicate `(request_id, region_id)` subscriptions, creates or reuses a `Delegate`, and subscribes the raftstore observer for new delegates. It then constructs an `Initializer` with snapshot/scan options and spawns it on the CDC worker runtime. The initializer later schedules `Task::InitDownstream` to synchronize capture-change response, send a barrier, and move the downstream into `Initializing`.

Raftstore observations arrive as `Task::MultiBatch`. The endpoint frees sink-memory quota already charged by the observer, then calls each region delegate. A delegate error marks it failed and becomes `Deregister::Delegate`, which broadcasts error events and removes connection subscriptions.

Resolved-ts is periodic. `register_min_ts_event` waits until the configured interval, obtains TSO from PD or causal-ts provider for API v2 RawKV, updates the concurrency manager, possibly lowers min-ts to `global_min_lock_ts`, resolves leader regions by either store RPC (`LeadershipResolver`) or raft command, schedules `Task::MinTs`, and re-registers the next event. `on_min_ts` delegates per-region advancement and emits grouped messages according to feature gates.

Deregistration is careful about stale IDs. Downstream teardown checks `DownstreamId`; delegate teardown checks `ObserveId`; connection/request/region teardown removes connection mappings and unsubscribes delegates. Removing the last downstream from a delegate stops observation and resets `txn_extra_op`.

`Task::TxnExtra` inserts old values into `OldValueCache` and frees the associated memory quota. Periodic timeout updates endpoint, region, resolved-ts, old-value cache, and sink memory metrics.

## State And Persistence Behavior

The endpoint keeps volatile CDC state only. Persistent data remains in TiKV engines and raftstore; CDC subscriptions are expected to be recreated by clients after failures or topology changes. Important volatile state includes:

- `capture_regions: HashMap<u64, Delegate>`: all observed regions.
- `connections: HashMap<ConnId, Conn>`: stream sinks and subscription indexes.
- `CdcObserver`: observer registry keyed by region/observe ID.
- Incremental scan runtime and counters/semaphore/limiters.
- `OldValueCache`: cached transaction old values delivered via `TxnExtra`.
- `current_ts`, `min_resolved_ts`, region counts, and gauges/histograms for metrics.
- `sink_memory_quota`: shared quota for CDC sink and transaction-extra scheduling.

Configuration changes mutate in-memory config and live helpers; they are validated through the `OnlineConfig` path before taking effect.

## Dependencies And Integration Points

- Raftstore: `CdcHandle`, `CmdBatch`, `ObserveId`, `StoreRegionMeta`, `CdcObserver`, and local read delegates.
- PD/resolved-ts: `PdClient`, feature gate for resolved-ts store RPC, `LeadershipResolver`, `resolve_by_raft`, and `ResolvedTsConfig`.
- TiKV storage: `LocalTablets`, `ConcurrencyManager`, `TxnExtra`, `TxnExtraScheduler`, CDC config structs.
- Async runtimes: Tokio workers for incremental scan and TSO/leadership resolution, `SteadyTimer`, futures compatibility.
- Service/channel layer: `Conn`, `FeatureGate`, `RequestId`, `validate_kv_api`, `CdcEvent`, sink errors.
- `initializer.rs` for snapshot capture and incremental scan.
- `delegate.rs` for per-region event conversion and resolved-ts gating.
- `metrics.rs` for endpoint, scan, connection, old-value, resolved-ts, sink, and task metrics.

## Risks And Edge Cases

- Registration has several partially completed states: connection subscription, delegate insertion, observer registration, and async initializer spawn. Error paths must remove the right pieces without invalidating newer subscriptions.
- The scan task counter is incremented before several early returns and released by a defer guard. This is necessary to avoid over-admission but must remain paired with every return path.
- `InitDownstream` relies on a force-sent barrier before invoking the raft callback; this ordering protects incremental scan from racing earlier delta changes.
- `register_min_ts_event` must never lose the leader resolver or fail to reschedule, otherwise resolved-ts advancement can stop. The code panics on schedule errors other than shutdown to surface this.
- `Advance::emit_resolved_ts` batches regions by increasing outlier counts. Incorrect heap ordering would regress the minimum resolved-ts reported to metrics or clients.
- Feature gates split protocol behavior between stream multiplexing, batch resolved-ts, and legacy per-region events; mixed-version clients remain a compatibility risk.
- Runtime and semaphore replacement on config updates can leave already-running scans above the new limit temporarily by design.
- `connections.get(...).unwrap()` in resolved-ts emission assumes delegates only contain downstreams for live connections; deregistration invariants must preserve this.
- Memory quota for `CdcTxnExtraScheduler` drops tasks on allocation failure and increments a metric, so old-value completeness relies on the cache/memory sizing path.

## Test Signals

Endpoint tests cover API-version compatibility, config hot updates, raftstore busy handling, registration duplicate/nonexistent-region/capture-change failures, too many scan tasks, RawKV causal min-ts, feature gates and legacy resolved-ts formats, deregistration stale-ID protection, batch resolved-ts across multiple connections, disconnect-before-delegate-ready behavior, resolved-region heap ordering, large resolved-ts batching, request/region multiplexing deregistration, and ignored registration after connection removal. These tests give strong state-machine coverage; remaining risk is mainly integration with real raftstore, PD/store-resolved-ts behavior, and production backpressure timing.
