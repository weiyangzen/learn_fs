# sources/storage-engines/foundationdb/fdbserver/datadistributor/DataDistribution.cpp

## Purpose
`DataDistribution.cpp` is the data-distributor runtime for FoundationDB. It bootstraps the active DD instance, loads persistent distribution metadata, resumes shard relocations and data moves, builds primary and remote team collections, runs the relocation queue and shard tracker, services DD interface requests, and coordinates adjunct workflows such as storage wiggling, bulk load, bulk dump, storage audits, snapshot creation, backup partition map generation, exclusion safety checks, and metrics queries.

The file is intentionally central: it wires together `DataDistributionTracker`, `DDQueue`, `DDTeamCollection`, `ShardsAffectedByTeamFailure`, `PhysicalShardCollection`, `BulkLoadTaskCollection`, `MoveKeysLock`, management API metadata, and storage server RPCs.

## Important APIs, Types, And Functions
`getDataMoveTypeFromDataMoveId` decodes a data move UID to determine logical/physical bulk-load versus ordinary movement behavior. `RelocateShard::setParentRange` and `getParentRange` store split parent metadata for write/size splits.

`DDAudit` wraps an `AuditStorageState` with an `ActorCollection`, retry counters, child-failure flags, a cancellation bit, task accounting, an `AsyncVar<int>` budget, context (`RESUME`, `LAUNCH`, `RETRY`), and a storage-server-shard audit progress cache. Its `cancel()` method cancels the core audit actor and clears children.

`StorageWiggler` methods maintain the wiggle priority queue and persisted wiggle metrics. `addServer`, `removeServer`, `updateMetadata`, and `getNextServerId` manage in-memory order; `necessary` enforces minimum server age unless the server is wrongly configured; `resetStats`, `restoreStats`, `startWiggle`, and `finishWiggle` persist metrics through `wiggleData`.

`DataDistributor` is the main reference-counted state object. It owns the database info, shared DD context, transaction processor, move-keys lock, database configuration, initial data distribution, team collections, relocation streams, bulk-load/dump managers, audit maps and locks, config-change watcher, actor sink, and readiness promise.

Major actor families include `DataDistributor::init`, `resumeFromShards`, `resumeFromDataMoves`, `dataDistribution`, `dataDistributor_impl`, `bulkLoadTaskCore`, `bulkLoadJobCore`, `bulkDumpCore`, `auditStorageCore`, `ddSnapCreateCore`, `monitorBackupPartitionRequired`, `monitorShardEncodeKnob`, `ddExclusionSafetyCheck`, and `ddGetMetrics`.

## Control Flow
Startup enters `dataDistributor_impl`, creates an actor collection, starts `dataDistribution`, and races the long-running distributor against interface requests. Non-mocked DD opens a server-side database and installs a `DDTxnProcessor`; mocked DD uses `DDMockTxnProcessor`.

`dataDistribution` initializes the configuration watcher before reading metadata so later changes trigger `dd_config_changed`. It loops through DD generations: waits for DD enablement, takes the move-keys lock, initializes audit metadata, waits out security mode, loads configuration, updates replica keys, reads initial distribution metadata, and either proceeds or emits disabled metrics and waits again.

After metadata load, the generation builds `ShardsAffectedByTeamFailure`, physical shard state, and bulk-load task collections; resumes existing shards and data moves; creates primary and optional remote `DDTeamCollection`s; creates `DataDistributionTracker` and `DDQueue`; wires relocation producer-to-consumer forwarding; starts optional physical-shard monitoring; starts bulk-load actors if enabled or a mode monitor if not; starts bulk-dump mode polling; starts periodic location-metadata audits and knob monitoring; then waits for all child actors. Expected DD restarts are driven by lock conflicts, configuration changes, and selected data movement errors.

Relocation resumption has two paths. `resumeFromShards` rebuilds shard ownership and health state from `InitialDataDistribution`, splits shards on custom boundaries unless bulk load disables boundary changes, registers teams in `ShardsAffectedByTeamFailure`, initializes physical shards when enabled, and schedules low-priority relocations for unhealthy, over-large, split, or anonymous-destination ranges. `resumeFromDataMoves` waits until shard resumption is complete, then replays persisted data moves: invalid, cancelled, bulk-load, or incompatible moves are emitted as cancellation relocations, while valid moves re-register destination teams and restart shard tracking before being sent to the relocation queue.

Bulk-load task execution persists a task through `Submitted`, `Triggered`, `Running`, `Complete`, `Acknowledged`, and `Error` phases in the bulk-load task range map. `scheduleBulkLoadTasks` scans task metadata, starts `doBulkLoadTask` under `bulkLoadEngineParallelismLimitor`, and erases acknowledged tasks. `doBulkLoadTask` persists trigger state, publishes the task into `BulkLoadTaskCollection`, sends `BulkLoadShardRequest` to the tracker/queue path, and waits for `BulkLoadAck`.

Bulk-load job execution converts one running job into many tasks. `bulkLoadJobManager` finds a running job, downloads and parses the job manifest into an ordered manifest map, persists task count, submits missing tasks with `bulkLoadJobNewTask`, monitors submitted tasks with `bulkLoadJobMonitorTask`, checks completion/error state, and finalizes by clearing task/job metadata, releasing the range lock, and adding the job to history.

Bulk dump is the mirror workflow for external export. `bulkDumpCore` polls bulk-dump mode, `bulkDumpManager` finds a submitted job, `scheduleBulkDumpJob` partitions job ranges by live shard locations and sends `BulkDumpRequest`s to chosen storage servers, `checkBulkDumpJobComplete` waits for all range-map entries to become complete, and the manager builds and uploads a global bulk-load-compatible job manifest before clearing metadata.

Audit control starts from `TriggerAuditRequest`. Launch and cancel paths use per-audit-type `FlowLock`s. `launchAudit` either returns a compatible existing audit ID or persists a new running audit and calls `runAuditStorage`. `runAuditStorage` constructs `DDAudit`, stores it in the audit map, and starts `auditStorageCore`. The core dispatches work, waits for child actors, verifies persisted progress, retries incomplete or failed child work, and persists final `Complete`, `Error`, or `Failed` audit states.

Audit dispatch is type-specific. HA, replica, and restore audits partition requested ranges by storage ownership and send `AuditStorageRequest`s to selected storage servers. Location-metadata audit reads KeyServers and ServerKeys in matching claim ranges, compares maps, rate-limits remote reads, and persists complete/error progress by range. Storage-server-shard audit schedules all-key checks on each non-TSS storage server and tracks servers already completed across retries.

Snapshot creation (`ddSnapCreateCore`) writes `writeRecoveryKey`, disables TLog pops, discovers stateful workers, snapshots storage workers with storage fault tolerance, snapshots TLogs with zero tolerance, re-enables TLog pops, snapshots coordinators, and clears the recovery flag. `ddSnapCreate` wraps this with DD enabled-state transitions, duplicate request/result maps, timeout handling, and recovery-change rejection.

Interface handling in `dataDistributor_impl` responds to halt, metrics, snapshot, exclusion safety, storage wiggler state, and audit trigger/cancel requests while the main distributor generation runs in the background.

## State And Persistence
Durable DD state is mostly FoundationDB system keyspace metadata accessed through `IDDTxnProcessor`, `ManagementAPI`, and KRM helpers. The file reads and writes the move-keys lock, database configuration, data-distribution mode, replica keys, server list, key servers/server keys, data-move keys and tombstones, bulk-load mode, bulk-load task and job range maps, bulk-load history, range locks, bulk-dump metadata, backup partition request/list keys, audit metadata and range/server progress, coordinator connection strings, and `writeRecoveryKey`.

In-memory generation state includes `DataDistributor::configuration`, `primaryDcId`, `remoteDcIds`, `initData`, `teamCollection`, relocation streams, actor collections, audit maps, bulk managers, task collections, and flags such as `bulkLoadEnabled`. Most in-memory state is reconstructed on DD restart from persistent metadata. Audit state is deliberately resumable: running audit records are loaded during `initAuditStorage`, and old finished records are cleaned in the background.

Local filesystem persistence is used only for bulk load/dump staging under the provided data-distributor folder: `ddBulkLoadFiles` and `ddBulkDumpFiles`. The code creates manifest temp folders, downloads job manifests, writes generated dump job manifests, uploads them through the selected transport, and best-effort clears local folders. Comments note TODOs for clearing those directories after crashes.

State consistency relies heavily on transaction options (`ACCESS_SYSTEM_KEYS`, `LOCK_AWARE`, `PRIORITY_SYSTEM_IMMEDIATE`), move-keys lock checks, DD enabled-state checks, range-map coalescing, and retry loops around transaction errors.

## Dependencies And Integration Points
The file depends on client metadata APIs (`Audit`, `AuditUtils`, `BulkLoading`, `BulkDumping`, `ManagementAPI`, `SystemData`, `RunRYWTransaction`), server-side DD components (`DataDistributor.h`, `DataDistribution.h`, `DDSharedContext`, `DDTeamCollection`, `DDRelocationQueue`, `MockDataDistributor`), core movement and recovery helpers (`MoveKeys`, `QuietDatabase`, `WaitFailure`, `BackupPartitionMap`, `BulkLoadUtil`, `BulkDumpUtil`), Flow actor primitives, counters, tracing, unit tests, and simulation fault injection.

External integration points include storage server RPCs (`auditStorage`, `bulkdump`, `getKeyValueStoreType`), worker snapshot RPCs, TLog disable/enable pop RPCs, cluster controller DD interface requests, range-lock registration for bulk load, locality/team-health decisions from team collections, and backup partition consumers watching `backupPartitionListKey`.

`MockDataDistributor::run` exposes the same runtime over a mock transaction processor for simulation tests. The two local `TEST_CASE`s cover storage wiggle order and shard-resume behavior.

## Risks
This file concentrates many long-running actors and restart paths. A missed budget increment in audit paths, bulk load/dump parallelism limiters, or actor cancellation can stall the DD. Several paths intentionally swallow non-cancellation errors to keep DD alive; that reduces blast radius but can leave zombie audit metadata, local bulk files, or work that only resumes after DD restart.

Bulk load and dump correctness depends on strict range-map invariants: adjacent range boundaries must match task/job ranges, task IDs must match persisted job IDs, and finalization must release locks only after metadata is safely acknowledged. Incorrect manifest ordering or partial manifest coverage can mark jobs unretryably failed.

DD startup must reconcile multiple sources of truth: initial shard metadata, user range config, existing data moves, physical shard metadata, bulk-load mode, and audit metadata. Misordering can produce duplicate relocation work, missed team-failure registration, or stale audit ownership.

Snapshot creation intentionally pauses recovery and TLog popping. Failures must re-enable pops and clear recovery state; network errors and duplicate snapshot IDs are handled, but partial worker snapshot success remains operationally sensitive.

Configuration changes and knob changes intentionally restart DD. If a new actor path does not include expected `dd_config_changed` or `movekeys_conflict` handling, it may either crash DD unnecessarily or continue with stale assumptions.

## Test Signals
Existing local tests exercise `StorageWiggler` queue ordering and `resumeFromShards` scheduling. Additional high-value signals are simulation tests for DD restart during audit creation, audit retry and cancellation, location metadata mismatches, bulk-load mode enabling after DD start, bulk-load task finalization with error tasks, bulk-dump manifest generation and upload, snapshot duplicate requests and timeout paths, exclusion safety checks with one team versus multiple teams, and configuration/knob changes during active data moves.

Trace events are a major operational test signal: `DDInit*`, `DDInitResumedDataMoves`, `DDBulkLoad*`, `DDBulkDump*`, `DDAudit*`, `SnapDataDistributor_*`, `DataDistributorConfigChanged`, and `DDShardEncodeKnobChanged` expose state transitions and failure classification.
