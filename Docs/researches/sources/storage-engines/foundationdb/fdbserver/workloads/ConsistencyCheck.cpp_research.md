# sources/storage-engines/foundationdb/fdbserver/workloads/ConsistencyCheck.cpp

## Purpose
`ConsistencyCheck.cpp` defines `ConsistencyCheck`, FoundationDB's broad cluster invariant workload. It can quiesce the database, suspend/resume based on a system key, validate storage/server metadata and role placement, check worker/coordinator lists, ensure consistency scan is stopped, and compare shard data across storage servers and TSS pairs.

## Important APIs, Types, And Functions
The main type is `ConsistencyCheckWorkload : TestWorkload`. Important helpers include `monitorConsistencyCheckSettings`, `runCheck`, `checkForUndesirableServers`, `checkStorageMetadata`, `checkForStorage`, `checkForExtraDataStores`, `checkWorkerList`, `checkCoordinators`, `checkUsingDesiredClasses`, `checkConsistencyScan`, `checkSingleSingleton`, and `checkSingleSingletons`. It also calls external helpers such as `quietDatabase`, `getDataDistributionQueueSize`, `getTeamCollectionValid`, `getTLogQueueInfo`, `getMaxStorageServerQueueSize`, `getKeyServers`, `getKeyLocations`, and `checkDataConsistency`.

## Control Flow
`setup` optionally quiets the database for quiescent checks and starts a monitor that watches `fdbShouldConsistencyCheckBeSuspended`. `_start` waits while suspended, then races one `runCheck` against suspension changes, repeating if `indefinite` is true. `runCheck` reads configuration and optional TSS mapping, performs quiescent-only queue/storage/worker/coordinator/role checks on the first client, then reads key server and key location metadata and calls `checkDataConsistency` across clients according to `distributed`, `shardSampleFactor`, `shuffleShards`, and rate-limit settings.

## State And Persistence
The workload mostly reads system state. It may write simulation state by disabling the timekeeper and setting `fdbSimulationPolicyState().quiesced`, and `checkForExtraDataStores` can reboot or kill simulated processes that have unexpected data stores. It maintains `success`, `repetitions`, `bytesReadInPreviousRound`, and the suspension `AsyncVar`.

## Dependencies And Integration Points
This file integrates with server DB info, data distributor, quiet database utilities, consistency scan config, TSS mapping utilities, storage server interfaces, coordinator connection strings, simulator process lists, process classes, and Flow `ProcessEvents` timeout reporting.

## Risks
The workload covers many moving cluster invariants and therefore contains numerous timing exceptions for recoveries, missing attributes, TSS recruitment, excluded processes, and region failover. In non-quiescent mode many deep checks are skipped. Some severe conditions call `testFailure` while other checks use `ASSERT`, so failure mode varies by invariant. The extra-data-store check can kill/reboot simulated processes, which is useful cleanup but can perturb concurrent workloads.

## Test Signals
Key traces include `ConsistencyCheckFailure`, `TestFailure`, `ConsistencyCheck_QuietDatabaseError`, `ConsistencyCheck_NonZeroDataDistributionQueue`, `ConsistencyCheck_TooManyTeams`, `ConsistencyCheck_NonZeroTLogQueue`, `ConsistencyCheck_WrongKeyValueStoreType`, `ConsistencyCheck_NoStorage`, `ConsistencyCheck_ExtraDataStore`, `ConsistencyCheck_WorkerMissingFromList`, `ConsistencyCheck_BadCoordinator`, role fitness traces such as `ConsistencyCheck_MasterNotBest`, and `ConsistencyCheck_FinishedCheck`. `check` returns the accumulated `success` flag.
