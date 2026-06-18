# sources/storage-engines/foundationdb/fdbserver/clustercontroller/ClusterRecovery.h

## Purpose
`ClusterRecovery.h` declares the shared data structures and public recovery functions used by the cluster controller and master recovery implementation. It defines recovery event types, coordinated-state helpers, and the `ClusterRecoveryData` state object that carries all mutable recovery context through the actor pipeline implemented in `ClusterRecovery.cpp`.

## Important APIs, Types, and Functions
- `ClusterRecoveryEventType` enumerates trace/event-cache categories for state, committed tlogs, duration, generation count, seed storage recruitment, invalid config, recovering/recovered config, snapshot checks, backup pausing, recovery commit, availability, and metrics.
- `recoveryTerminateOnConflict()` and `getRecoveryEventName()` are declared here for recovery conflict handling and trace naming.
- `ReusableCoordinatedState` wraps `MovableCoordinatedState` with recovery-specific read/write behavior, previous/current `DBCoreState`, conflict monitoring, final-write semantics, and coordinator movement.
- `ClusterRecoveryData` is a reference-counted, non-copyable aggregate carrying controller pointers, db id, versions, configuration, coordinators, log system handles, transaction-state storage, recruited role interfaces, master identity, recovery promises/triggers, counters, and event cache holders.
- `recruitNewMaster()`, `cleanupRecoveryActorCollection()`, `clusterRecoveryCore()`, and `isNormalClusterRecoveryError()` are the main exported functions for the cluster-controller recovery loop.

## Control Flow
`ReusableCoordinatedState::read()` reads raw coordinator state, deserializes `DBCoreState`, initializes `prevDBState`/`myDBState`, and registers a conflict actor via `addActor`. `write()` serializes a new `DBCoreState` with the appropriate protocol feature version, writes it exclusively, updates `myDBState`, and either rereads to verify non-final writes or sends `fullyRecovered` for final writes.

`ClusterRecoveryData` is constructed by the cluster-controller recovery actor before `clusterRecoveryCore()` runs. The constructor initializes version fields to invalid values, creates recovery triggers/promises, sets up counters and event cache holders, and starts counter tracing. It also rejects forced recovery if no cluster-controller dc ID is available.

The destructor closes `txnStateStore` if it was opened during recovery. Other cleanup is actor-driven through `cleanupRecoveryActorCollection()` in the implementation.

## State and Persistence Behavior
`ReusableCoordinatedState` is the header's main persistence-sensitive type. It protects coordinated-state writes with `finalWriteStarted` so no further writes can proceed after a final write begins. Non-final writes deliberately reset `MovableCoordinatedState`, reread, compare against the written state, and install a fresh conflict monitor. This makes cstate changes act as a recovery fencing mechanism.

`ClusterRecoveryData` stores both durable-state mirrors and transient runtime state:
- Durable mirrors: `lastEpochEnd`, `recoveryTransactionVersion`, `versionEpoch`, `liveCommittedVersion`, `minKnownCommittedVersion`, `originalConfiguration`, `configuration`, `coordinators`, `dcId_locality`, `allTags`, and `cstate`.
- Runtime handles: `logSystem`, `txnStateLogAdapter`, `txnStateStore`, recruited proxies/resolvers/backup workers, provisional proxies, and `lastCommitProxyVersionReplies`.
- Control promises: `registrationTrigger`, `recoveryReadyForCommits`, `cstateUpdated`, `addActor`, and `recruitmentStalled`.
- Observability state: counters and event cache holders for metacluster metadata, software-version compatibility, recovered config, recovery state, generations, duration, availability, and metrics.

## Dependencies and Integration Points
The header depends on core FoundationDB server types: `DatabaseContext`, replication utilities, coordinated state, coordinator interfaces, `ClusterController.h`, `DBCoreState`, knobs, key-value stores, log systems, log-system disk queues, worker interfaces, Flow coroutines, errors, and system monitoring. It ends by including `MoveKeys.h`, making move-key types available to users of the header.

`ClusterRecoveryData` integrates directly with `ClusterControllerData`, `ServerDBInfo`, `MasterInterface`, `ClusterControllerFullInterface`, `ServerCoordinators`, and transaction-system role interfaces. The public declarations are consumed by the cluster controller code that recruits masters and runs `clusterRecoveryCore()`.

## Risks and Edge Cases
- `ClusterRecoveryData` is intentionally broad and mutable. Most fields are shared across asynchronous actors, so ordering is enforced by promises, actor cancellation, and state-machine phases rather than encapsulation.
- `ReusableCoordinatedState::_write()` parks forever if a write is attempted after a final write starts, which is correct for fencing but can make misuse look like a hang.
- Serialization protocol selection depends on `SERVER_KNOBS->RECORD_RECOVER_AT_IN_CSTATE`; mixed-version or feature-removal changes require care because coordinated-state bytes must stay readable by recovery participants.
- Forced recovery safety depends on the constructor check for `clusterControllerDcId`; callers should not assume `forceRecovery` remains true after construction.
- `txnStateStore` ownership is raw-pointer based and closed in the destructor, while `txnStateLogAdapter` is stored as a raw pointer managed by the adapter/store flow; lifetime assumptions are important.

## Test Signals
Tests and simulation can assert state through recovery trace event names, `ClusterRecoveryData` counters, and cstate conflict behavior. Important observable signals include `RecoveryTerminated` with conflict or cstate-change reasons, event-cache updates for recovery state/generations/duration/availability, counter collection logs under `RecoveryMetrics`, and forced recovery rejection via `ForcedRecoveryRequiresDcID`.
