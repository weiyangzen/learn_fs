# sources/storage-engines/tikv/components/raftstore-v2/src/worker/pd/mod.rs

Purpose: this file defines the raftstore-v2 PD worker task enum, runner state, runnable dispatch, reporter adapters, and admin-request helper constructors.

Important APIs/types/functions: `Task` covers store heartbeat/info updates, region heartbeat/stat updates, split operations, max timestamp update, bucket/min-resolved-ts reports, slowness inspection, and graceful shutdown state. `Runner<EK, ER, T>` owns PD client, raft engine, tablet registry, snap manager, store router, stats monitor, YATP remote, store/region stats, CPU records, concurrency manager, optional causal ts provider, slowness stats, gRPC service manager, config, and shutdown flags. `PdReporter` implements `FlowStatsReporter`, `Collector`, and `StoreStatsReporter`. `requests` builds and sends admin requests.

Control flow: `Runner::new` configures `PdStatsMonitor`, starts it with auto-split and resource collectors, and initializes state maps. `Runnable::run` schedules the heartbeat response receiver and dispatches every `Task` to specialized handlers in `store`, `region`, `split`, `misc`, or `slowness`. Reporter trait methods convert stats-monitor callbacks back into PD worker tasks.

State and persistence: PD worker stores accumulated store/region statistics, bucket deltas, CPU records, heartbeat timing, and slowness trends in memory. It does not directly persist raft data; admin requests are routed back to peers for raft proposal.

Dependencies/integration: integrates PD client, resource metering collector, auto split controller, gRPC service manager, config version track, store router, and raftstore store stats traits.

Risks: the runner is a hub; dropped scheduled tasks lose stats or management actions. `maybe_schedule_heartbeat_receiver` must run once to receive PD operators. Admin helper sends best-effort and logs failures rather than retrying locally.

Test signals: no direct tests in this file. Submodules include targeted tests; integration coverage should verify PD worker dispatch and heartbeat response handling.
