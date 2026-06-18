# sources/storage-engines/foundationdb/fdbserver/logsystem/include/fdbserver/logsystem/LogSystem.h

## Purpose
Declares the central FoundationDB log-system API: push-side message construction, log epoch state, recovery and epoch transitions, log-set routing, pop tracking, TLog locking/durable-version computation, and the peek cursor base interfaces used by consumers.

## Important APIs, Types, And Functions
`IPeekCursor` defines sequential log-consumption operations. `IReplayPeekCursor` adds replay-specific location, max-known-version, clone, and advance operations. `LogPushData` batches tagged log messages and encodes span/transaction info. `OldLogData`, `IdToInterf`, `LogLockInfo`, and `DurableVersionInfo` model old epochs, lock replies, and durability policy results. `LogSystem` exposes construction from configs, `recoverAndEndEpoch()`, `newEpoch()`, `push()`, `makeConsumer()`, pop helpers, backup-worker mutation, rejoin tracking, durable version helpers, and `getRecoverVersionUnicast()`.

## Control Flow
Callers construct a `LogSystem` from core state/log-system config, build `LogPushData`, route tags to TLogs through log-set location helpers, and call `push()` with a `LogPushVersionSet`. Consumers obtain a `LogSystemConsumer` for peeking and popping. During recovery, old state is converted to a log system, TLogs are locked, durable/recover versions are computed, old generations are purged, and a new epoch is recruited/written back to core state.

## State And Persistence Behavior
`LogSystem` carries epoch-local and old-generation state: TLog sets, router/TXS tag counts, pseudo-localities, recovery futures, recovered-version variables, lock results, known locked/stopped TLog IDs, recover-at/recovered-at versions, known committed version, backup start version, pop actors, outstanding pops, old log data, and backup-worker tags. Template `LogPushData::writeTypedMessage()` serializes messages with length, subsequence, tags, optional remote router tag, and span context into per-location binary writers.

## Dependencies And Integration Points
The header depends on database configuration, replication/locality policy, backup progress, DBCoreState, mutation tracking, span context messages, TLog interfaces, WorkerInterface, Flow actor/future utilities, histograms, and knobs. It is used by commit proxies, GRV proxies, resolvers, cluster recovery, backup workers, TLog servers, and logsystem implementation files.

## Risks And Edge Cases
Correctness relies on matching replication policy, locality routing, pop semantics, old epoch history, pseudo-locality mapping, and remote/satellite log behavior. `LogPushData::writeTypedMessage()` reuses serialized bytes across locations after writing the first copy, so writer offsets and message lengths are critical. Recovery code must distinguish known committed, durable, minimum durable, recover-at, and stopped/locked TLog states. Raw pointers and actor futures in `LogSystem` make lifetime and shutdown ordering important.

## Test Signals
Signals include log-system unit tests, recovery simulation tests, `LogSystemRecoveryTests.cpp`, transaction-state recovery, proxy commit-path tests, and traces around push, epoch end, lock replies, rejoin tracking, and durable-version computation.
