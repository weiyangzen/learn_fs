# sources/storage-engines/tikv/components/raftstore/src/store/worker/pd.rs

## Purpose
This file implements the raftstore PD worker: the asynchronous bridge between local raftstore state and the placement driver (PD). It reports region and store heartbeats, asks PD for split IDs, receives PD scheduling decisions, validates stale peers, forwards PD-directed admin commands into raftstore, reports read/write/store/CPU/bucket statistics, updates slow-score health data, controls gRPC serving state, and coordinates unsafe recovery and graceful shutdown state.

It also owns `StatsMonitor`, a side thread that periodically samples process/thread statistics, feeds the auto-split controller, and schedules latency inspection tasks back to the PD worker.

## Important APIs, Types, and Functions
`FlowStatistics`, `ReadStats`, and `WriteStats` integration is exposed through `FlowStatsReporter`, whose `Scheduler<Task<EK>>` implementation wraps read/write flow reports into PD worker tasks.

`HeartbeatTask` contains the region-heartbeat payload collected by peers: term, region, leader peer, down/pending peers, written bytes/keys, approximate size/keys, replication status, and waiting-data peers.

`Task<EK>` is the central work enum. Important variants include split requests (`AskSplit`, `AskBatchSplit`, `AutoSplit`), PD heartbeats (`Heartbeat`, `StoreHeartbeat`), split/peer validation (`ReportBatchSplit`, `ValidatePeer`), metric ingestion (`ReadStats`, `WriteStats`, `StoreInfos`, `RegionCpuRecords`, `ReportBuckets`), lifecycle hooks (`DestroyPeer`, `GracefulShutdownState`), timestamp safety (`UpdateMaxTimestamp`), query/latency/control paths (`QueryRegionLeader`, `UpdateSlowScore`, `InspectLatency`, `ControlGrpcServer`), and resolved-ts reporting.

`StoreStat` tracks store-wide cumulative and last-reported counters: engine read bytes/keys/query stats, last capacity/used/available bytes, histogram locals for region read/write rates, sampled CPU and IO rate records, and CPU busy thresholds. `PeerStat` tracks per-region cumulative read/write/query/cop statistics plus last region-heartbeat and store-heartbeat baselines. `ReportBucket` stores current and previously reported bucket stats and emits deltas.

`StatsMonitor<T>` starts/stops the stats sampling thread. `collect_store_infos()` samples `ThreadInfoStatistics`; `load_base_split()` flushes the auto-split controller, read stats, and CPU stats into split recommendations; `maybe_send_read_stats()` and `maybe_send_cpu_stats()` use bounded sync channels so the monitor cannot accumulate unbounded memory.

`Runner<EK, ER, T>` is the PD worker `Runnable`. It stores the PD client, raft router, shared per-region stats map, bucket stats, store stats, stats monitor, heartbeat interval, CPU-record accumulators for region and store heartbeats, concurrency manager, snapshot manager, async runtime remote, health reporter/controller, coprocessor host, optional causal timestamp provider, gRPC service manager, graceful-shutdown flag, and split validator.

Helper constructors build raft admin requests: `new_change_peer_request()`, `new_change_peer_v2_request()`, `new_split_region_request()`, `new_batch_split_region_request()`, `new_transfer_leader_request()`, `new_merge_request()`, and `new_batch_switch_witness()`. `send_admin_request()` wraps those into `RaftCommand`s and sends them through `RaftRouter`; `send_destroy_peer_message()` sends a tombstone raft message for stale peers.

## Control Flow
`Runner::new()` initializes store CPU quota thresholds, starts `StatsMonitor`, creates the health reporter, initializes all accumulators, and captures service/control dependencies. The first call to `run()` lazily schedules `schedule_heartbeat_receiver()`, which subscribes to PD region-heartbeat responses and converts PD operators into local actions: change peer, change peer v2, transfer leader, split, merge, witness switching, or auto-split enable/disable.

Split tasks call PD asynchronously through `ask_split()` or `ask_batch_split()`. On success, the worker sends a split admin request to raftstore. If `ask_batch_split()` returns `Error::Incompatible`, it falls back to single-key `AskSplit` for rolling-upgrade compatibility. Load-based split callbacks update load-split success/failure metrics.

`Task::Heartbeat` computes per-region deltas from `PeerStat`, consumes the region's CPU record from `region_cpu_records_since_region_heartbeat`, updates last-report baselines, and calls `handle_heartbeat()` to send `pd_client.region_heartbeat()` asynchronously. `Task::StoreHeartbeat` calls `handle_store_heartbeat()`, which consumes store-heartbeat peer deltas and CPU records for real heartbeats, computes hotspot peer stats, fills store capacity/usage/read/query/CPU/IO/slow-score/gRPC/shutdown fields, and sends `pd_client.store_heartbeat()`. Store-heartbeat responses can update replication mode, execute unsafe recovery plans, awaken hibernated regions in batches, schedule gRPC pause/resume, and mark the snapshot manager offline/serving based on PD node state.

`Task::ReadStats` and `Task::WriteStats` update cumulative store and peer counters. Read stats also merge bucket data and feed `StatsMonitor` for auto-split. `Task::RegionCpuRecords` sends raw records to the auto-split lane and accumulates CPU time into both region-heartbeat and store-heartbeat maps. `Task::ReportBuckets` merges bucket stats and reports a delta to PD.

Latency inspection is driven by `StatsMonitor` scheduling `InspectLatency`. `handle_inspect_latency()` ticks the health reporter, may force a fake store heartbeat when raft disk slow score reporting is delayed, builds a `LatencyInspector`, and sends a `StoreMsg::LatencyInspect` into raftstore. The async inspector callback schedules `UpdateSlowScore`, where the worker records measured durations.

`UpdateMaxTimestamp` loops asynchronously while the region's `TxnExt.max_ts_sync_status` remains at the initial value. It either flushes a rawkv v2 causal timestamp provider or fetches a TSO from PD, then updates `ConcurrencyManager::update_max_ts()` and marks the status as synced with a compare-exchange.

## State and Persistence Behavior
Most state is in memory and is deliberately delta-based. `PeerStat` and `StoreStat` cumulative counters are never persisted by this worker; heartbeat handlers store "last reported" snapshots so PD receives interval deltas. Destroyed peers are removed from `region_peers` and both CPU accumulator maps by `remove_peer_stat_from_maps()`.

CPU records have two independent lifetimes. Region-heartbeat records are consumed by individual region heartbeats; store-heartbeat records are consumed by real store heartbeats. Fake store heartbeats intentionally do not consume peer deltas or CPU records, preserving the next real heartbeat's full interval.

Bucket reporting keeps current bucket stats plus the last reported bucket metadata/stats. `ReportBucket::new_report()` recalculates old stats against current metadata before subtracting, handling bucket boundary changes.

Persistent effects occur through external systems rather than local files: PD heartbeats and reports mutate PD's cluster view; raft admin requests are proposed through raftstore and persisted by raft consensus/apply paths; unsafe recovery and tombstone messages are routed into raftstore; gRPC pause/resume changes service state; `UpdateMaxTimestamp` updates the concurrency manager's max timestamp for correctness after leader movement or rawkv v2 causal timestamp flush.

`collect_engine_size()` delegates to `CoprocessorHost` observers when available, otherwise reads disk capacity/usage/availability from the host. Snapshot manager offline state is toggled from PD store node state.

## Dependencies and Integration Points
The worker depends heavily on `pd_client::PdClient` for split ID allocation, region/store heartbeats, heartbeat-response streaming, resolved-ts reports, region lookups, and leader queries. `RaftRouter` is the local integration point for admin commands, casual messages, store control messages, latency inspection, unsafe recovery actions, and raft tombstones.

Stats and load-split integration spans `AutoSplitController`, `AutoSplitControllerContext`, `SplitValidator`, `ThreadInfoStatistics`, `resource_metering::{Collector, RawRecords, RegionCpuRecord}`, `TopN`, and raftstore worker metrics. Health integration uses `health_controller::{HealthController, RaftstoreReporter, LatencyInspector, InspectFactor}`.

Coprocessor hooks include `on_region_heartbeat()` and `on_compute_engine_size()`. Timestamp safety integrates with `ConcurrencyManager`, `CausalTsProviderImpl`, `TxnExt`, and PD TSO. Runtime async work is spawned on a `yatp::Remote`.

PD response operations integrate with raftstore admin command builders and `StoreMsg` variants. Unsafe recovery integrates with `UnsafeRecoveryForceLeaderSyncer`, `UnsafeRecoveryExecutePlanSyncer`, and `UnsafeRecoveryHandle`. Service control integrates with `GrpcServiceManager` and global readiness state.

## Risks and Edge Cases
Heartbeat data is delta-based, so incorrect baseline updates can under-report or double-report load. The file deliberately treats fake store heartbeats differently from real ones; changing that distinction could consume CPU/read deltas prematurely and hide a full interval from PD.

CPU accounting is approximate and path-specific. Region CPU records only include outside RPC workloads, and the write path currently accounts mainly lock checking. Store-heartbeat hotspot admission uses unified-read CPU for read hotspots and reports scheduler CPU separately; folding scheduler CPU into admission would change PD hotspot behavior.

The stats monitor uses bounded channels and drops samples when full. This prevents memory buildup but means auto-split and CPU-based decisions can miss data under sustained pressure. Tick interval math skips monitoring when configured intervals become too small, especially under failpoint/test settings.

Asynchronous PD operations can race local region changes. Split requests use a `SplitValidator` to disable some load splits, but stale regions, epoch changes, PD incompatibility, or router send failures still need to be handled by callbacks and metrics. Heartbeat response handling assumes PD response ordering and region epochs are sufficient to safely convert operators to local commands.

`UpdateMaxTimestamp` loops until status changes or succeeds; repeated PD/causal-provider failures log periodically but keep retrying. Service pause/resume from PD can make local availability depend on health-controller state and PD decisions.

## Test Signals
In-file tests cover stats monitor collection, top-N hotspot peer selection, CPU threshold admission, orphan CPU-record cleanup, zero-interval CPU handling, unified-read versus scheduler CPU treatment, CPU accumulation before rounding, report interval start fallback, peer-stat removal, region CPU record aggregation by store/region, bucket delta recalculation across boundary changes, coprocessor-provided engine size, and bounded stats monitor channels.

Additional useful signals are integration tests for PD heartbeat response operators, split fallback on incompatible PD, fake versus real store heartbeat delta preservation, unsafe recovery routing, gRPC pause/resume, max-ts retry and stale-status behavior, and load-split callback metrics.
