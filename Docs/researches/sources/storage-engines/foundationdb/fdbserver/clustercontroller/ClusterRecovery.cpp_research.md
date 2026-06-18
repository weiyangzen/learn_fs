# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterRecovery.cpp

## Purpose
`ClusterRecovery.cpp` implements the cluster-controller side of FoundationDB database recovery. It recruits a new master/sequencer and transaction system roles, locks and updates coordinated state, recovers transaction state from the previous log system epoch, starts a new log epoch, writes the recovery transaction, registers the recovered master with the cluster controller, and keeps registration/coordinated-state metadata current until the next recovery. This file is the active state-machine implementation behind the contracts declared in `ClusterRecovery.h`.

## Important APIs, Types, and Functions
- `normalClusterRecoveryErrors()` and `isNormalClusterRecoveryError()` define the error set treated as expected recovery turnover, including failed proxies/resolvers/tlogs, recruitment exhaustion, coordinator conflicts, worker removal, and recovery timeout/failure paths.
- `recoveryTerminateOnConflict()` races coordinated-state conflict against state switching and throws `worker_removed` when another recovery wins before this one becomes fully recovered.
- `recruitNewMaster()` recruits the master in the cluster-controller data center, updates `masterProcessId`, increments unfinished recovery accounting, and handles forced master failure/retry behavior.
- `clusterRecruitFromConfiguration()` and `clusterRecruitRemoteFromConfiguration()` wrap cluster-controller worker selection with retry/queue behavior for primary and remote recruitment.
- `newCommitProxies()`, `newGrvProxies()`, `newResolvers()`, `newTLogServers()`, and `newSeedServers()` initialize all transaction-system roles for the new epoch.
- `trackTlogRecovery()` continuously writes evolving `DBCoreState` to coordinators while old generations are purged and new logs become fully committed.
- `changeCoordinators()`, `configurationMonitor()`, `updateRegistration()`, `sendMasterRegistration()`, and `updateLogsValue()` keep cluster metadata, master registration, and coordinator state aligned after recovery.
- `ProvisionalMaster` and `provisionalMaster()` create provisional proxy endpoints during stalled recovery so emergency configuration transactions can be accepted and merged into the eventual recovery transaction.
- `monitorInitializingTxnSystem()` enforces an exponential-backoff timeout for transaction-system initialization.
- `recruitEverything()`, `readTransactionSystemState()`, `sendInitialCommitToResolvers()`, `recoverFrom()`, and `clusterRecoveryCore()` form the primary recovery pipeline.
- `getRecoveryEventName()` centralizes recovery trace event names using a knob-controlled prefix for compatibility with tooling.

## Control Flow
The top-level flow starts in `clusterRecoveryCore()`. It begins a recovery trace interval, adds master failure monitoring, sets the recovery state to `READING_CSTATE`, and reads coordinated state through `ReusableCoordinatedState`. Protocol compatibility is checked before the code transitions to `LOCKING_CSTATE`.

Recovery then calls `recoverAndEndLogSystemEpoch()` to stop the prior log epoch and obtains changing `oldLogSystems` as recovery discovers or replaces log systems. The core state recovery count is incremented, protocol-version fields may be updated, and the new state is written back to coordinators. This early write is raced with epoch-ending work so coordinator conflicts displace the current recovery promptly.

Once an old log system is available, `recoverFrom()` reads the old transaction system state by opening a `LogSystemDiskQueueAdapter` and `IKeyValueStore` over the old log system. It computes `lastEpochEnd`, `recoveryTransactionVersion`, reads persisted configuration, tag locality mappings, server tags, history tags, version epoch, and minimum required commit version. Forced recovery narrows tags/locality to the safe locality and mutates configuration to one usable region in the local data center.

`recoverFrom()` then starts `recruitEverything()`. In parallel, after a configured delay, a `ProvisionalMaster` exposes provisional commit and GRV proxy interfaces. If normal recruitment finishes first, any generated configuration changes are merged into the pending recovery transaction. If an emergency transaction arrives first, the code validates it as a configuration-affecting transaction, applies it to `self->configuration`, resets `initialConfChanges`, re-applies forced recovery constraints when needed, and restarts recruitment if the configuration changed.

`recruitEverything()` validates configuration, recruits workers from `ClusterControllerData`, records primary/remote dc IDs, initializes seed storage servers for a brand-new database, then initializes commit proxies, GRV proxies, resolvers, and the new log epoch concurrently. Initialization is raced against `monitorInitializingTxnSystem()`, which scales timeout by unfinished recovery count. After all roles initialize, the master interface receives `UpdateRecoveryDataRequest`.

After recruitment, `clusterRecoveryCore()` asserts minimum role counts and writes the recovery transaction. For existing databases it sets `lastEpochEndKey` first, handles snapshot restore markers, pause-backup mutations, forced recovery kill/reboot/lock-owner mutations, and coordinator/log/datacenter metadata. For a new database it seeds initial shard servers as the first transaction at version 1. Configuration changes from normal recruitment or emergency transactions are appended early but after the required `lastEpochEndKey` ordering. The transaction is sent through the first commit proxy, while transaction state is broadcast to commit proxies and optionally resolvers, and resolvers receive an initial resolve batch through `sendInitialCommitToResolvers()`.

After the recovery commit and transaction-state broadcast finish, the code starts `trackTlogRecovery()`. That actor writes new log-system core state, purges old recovered generations only after durable cstate writes, sends `cstateUpdated` and `recoveryReadyForCommits`, and advances recovery state through `ALL_LOGS_RECRUITED`, `STORAGE_RECOVERED`, and `FULLY_RECOVERED`. `clusterRecoveryCore()` waits for `cstateUpdated`, records recovery duration/availability events, enters `ACCEPTING_COMMITS`, starts coordinator-change/configuration-monitor actors, starts backup/range-backup workers if configured, and then waits forever until failure or cancellation.

## State and Persistence Behavior
Recovery persists and validates multiple state layers:
- Coordinated state stores `DBCoreState`, recovery count, protocol compatibility, tlog generations, and final recovery completion. `ReusableCoordinatedState` writes through `MovableCoordinatedState::setExclusive()` and rereads non-final writes to detect conflicting masters.
- Transaction state is recovered from the old log system into `txnStateStore`, then selectively updated by applying recovery metadata mutations before the recovery commit is sent.
- Version state is derived from old log end, `MAX_VERSIONS_IN_FLIGHT`, forced recovery knobs, `versionEpochKey`, `minRequiredCommitVersionKey`, and simulation buggify paths.
- Configuration state is read from `configKeys`, modified by emergency transactions or forced recovery, serialized into the recovery transaction, and watched after recovery by `configurationMonitor()`.
- Log metadata is stored through `logsKey`, log-system core state, `tagLocalityListKeys`, `serverTagKeys`, `serverTagHistoryKeys`, `tLogDatacentersKeys`, `primaryLocalityKey`, coordinator keys, and backup version keys.
- `trackTlogRecovery()` deliberately delays in-memory old-generation purge until after durable cstate writes to avoid losing old tlog references before a future recovery can lock them.
- `discardCommit()` consumes and acknowledges the transaction-state store's pending commit message without persisting it as a real committed recovery-side write.

## Dependencies and Integration Points
This file ties together cluster-controller worker recruitment, master interfaces, transaction proxies, resolvers, tlogs, storage-server seeding, log-system epoch management, backup progress, coordinator movement, system-key encoding, and Flow actors/coroutines. Major dependencies include `ClusterControllerData`, `MasterInterface`, `WorkerInterface`, `DatabaseConfiguration`, `DBCoreState`, `LogSystem`, `LogSystemConfig`, `LogSystemDiskQueueAdapter`, `IKeyValueStore`, `BackupProgress`, `applyMetadataMutations()`, `seedShardServers()`, and Flow primitives such as `Future`, `Promise`, `AsyncVar`, `race`, `getAll`, and `TraceEvent`.

External integration is mostly via RPC endpoints: worker recruitment endpoints, proxy initialization endpoints, resolver initialize/resolve endpoints, tlog rejoin, master registration, change-coordinators request stream, and provisional proxy endpoints. Operational tooling integrates through `TraceEvent` names, `EventCacheHolder` tracking keys, recovery status codes, and counters maintained on `ClusterRecoveryData`.

## Risks and Edge Cases
- Correctness relies on strict ordering of the recovery transaction, especially placing `lastEpochEndKey` first for existing databases and preserving `COMMIT_ON_FIRST_PROXY` assumptions by storing the first commit proxy at index 0.
- Coordinated-state conflict handling is subtle: non-final writes reread state and can throw `worker_removed`, while final writes send `fullyRecovered` and stop conflict termination.
- Too many old generations can delay or stop recovery, and simulation may disable connection failures to make the condition diagnosable.
- Forced recovery mutates usable regions, kills unsafe storage locality, and writes reboot/lock-owner markers. Misuse can intentionally sacrifice unavailable regions and requires the cluster-controller dc ID.
- Provisional master emergency transactions are intentionally narrow and ignore read conflict ranges. The code prevents `usable_regions` changes after an initialized original configuration, but other configuration mutations still affect recruitment.
- Initialization timeout parameters are validated and can park forever if invalid or if unfinished recoveries exceed a configured ceiling.
- `getRecoveryEventName()` contains a duplicate `CLUSTER_RECOVERY_SS_RECRUITMENT_EVENT_NAME` insertion for `"RecoverySnapshotCheck"` after a correct snapshot insertion. Because `std::map::insert` does not overwrite, this appears harmless but is a maintenance hazard.
- Backup/range-backup recruitment depends on persisted backup progress and minimum backup version filtering. Incorrect progress interpretation can under- or over-recruit old backup work.

## Test Signals
The file is heavily instrumented for simulation and operational testing: `CODE_PROBE`, `buggify()`, `TraceEvent` recovery status transitions, debug restored-version checks, simulation-only max-generation behavior, assertions on role counts and state invariants, and normal-error classification. Useful test signals include successful transitions through `reading_coordinated_state`, `locking_coordinated_state`, `reading_transaction_system_state`, `initializing_transaction_servers`, `recovery_transaction`, `writing_coordinated_state`, `accepting_commits`, and ultimately `fully_recovered`; timeout traces from `monitorInitializingTxnSystem()`; and recovery commit traces/errors.
