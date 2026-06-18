# sources/storage-engines/foundationdb/fdbserver/storageserver/include/fdbserver/storageserver/StorageServer.h

## Purpose
`StorageServer.h` declares the two public actor entry points for running a FoundationDB storage server on a worker. One overload initializes a newly recruited storage server, and the other recovers an existing storage server from an already opened key-value store. The implementation in `storageserver.actor.cpp` owns the long-running storage-server state machine, persistence recovery, interface registration, read and mutation-serving actors, metrics, data movement, change feeds, watches, checkpointing, and shutdown cleanup.

The header is intentionally small because `StorageServer` itself is a large internal struct in the actor implementation. External worker code only needs to spawn the actor with the correct persistent store, network interface, cluster state, folder paths, and recruitment/recovery promises.

## Important APIs, Types, and Functions
- `Future<Void> storageServer(IKeyValueStore* persistentData, StorageServerInterface ssi, Tag seedTag, Version startVersion, Version tssSeedVersion, ReplyPromise<InitializeStorageReply> recruitReply, Reference<AsyncVar<ServerDBInfo> const> db, std::string folder)` starts a newly recruited storage server. It initializes the key-value store, registers or adopts a tag, makes new server metadata durable, replies to the recruiter with `InitializeStorageReply`, and then enters `storageServerCore`.
- `Future<Void> storageServer(IKeyValueStore* persistentData, StorageServerInterface ssi, Reference<AsyncVar<ServerDBInfo> const> db, std::string folder, Promise<Void> recovered, Reference<IClusterConnectionRecord> connRecord)` starts an existing storage server during worker recovery. It initializes and commits the store, restores durable state, registers the recovered interface, resolves memory-store removal races, signals `recovered`, and then enters `storageServerCore`.
- Forward declarations keep this public header light: `IClusterConnectionRecord`, `IKeyValueStore`, `InitializeStorageReply`, and `ServerDBInfo`.
- Included types from `fdbclient/StorageServerInterface.h` and `flow/flow.h` provide `StorageServerInterface`, `Tag`, `Version`, `ReplyPromise`, `Promise`, `Reference`, `AsyncVar`, and `Future`.

## Control Flow
Worker code opens or reuses an `IKeyValueStore`, builds a `StorageServerInterface`, and calls the appropriate overload. For new recruitment, `worker.actor.cpp` passes seed tag and initial cluster versions from the recruitment request and wires the returned future through I/O error handling and rollback reboot logic. For recovery, worker startup iterates existing stores and calls the recovery overload, collecting the `recovered` promises so process startup can wait for durable state restoration.

In the new-server path, the implementation constructs an internal `StorageServer self`, sets shard-aware mode, handles TSS pairing if needed, initializes and commits the storage engine, creates checkpoint directories, clears bulk dump/load scratch folders, and either calls `addStorageServer()` to allocate a fresh tag or uses the supplied seed tag. It persists new-storage-server metadata with `makeNewStorageServerDurable()`, starts interface registration, sends `InitializeStorageReply`, initializes byte-sample recovery to `Void()`, then runs `storageServerCore(&self, ssi)`.

In the recovery path, the implementation reconstructs folder subpaths, ensures checkpoint folders exist, clears transient bulk folders, starts RocksDB log cleanup, initializes and commits the storage engine, races memory-store commit against `memoryStoreRecover()` to handle servers that should be removed, calls `restoreDurableState()`, validates TSS identity, publishes `recovered`, registers the interface, and then runs the same `storageServerCore`.

`storageServerCore` starts the major service actors: update processing, metrics, read request streams, watches, change feeds, shard-state and checkpoint handlers, storage audits, bulk dump/load handling, consistency checks, tag measurement intervals, and queue-metric handling. It then loops on database-info changes, tlog update progress, endpoint requests, and actor failures.

## State and Persistence Behavior
The header's parameters define the persistence boundary. `persistentData` is the durable `IKeyValueStore` owned by the storage server actor until termination. The new path persists server identity and metadata by calling `makeNewStorageServerDurable()` and committing before replying to recruitment. The recovery path reads persisted durable state through `restoreDurableState()` and may return early if no valid durable storage server state exists.

The implementation stores and restores versions, tags, shard metadata, byte sample data, TSS quarantine state, checkpoint metadata, and mutation-log application state. `folder` is used to derive checkpoint, fetched-checkpoint, bulk dump, and bulk load directories; checkpoint directories are created if missing, and transient bulk directories are cleared on start. Termination closes, disposes, or leaves the key-value store depending on error code: worker removal and recruitment failure dispose persistent data, reboot leaves it alone, and most other exits close it.

The actor publishes its network endpoints through `StorageServerInterface`. Registration updates system keys such as server list, server tag, tag history, and TSS mappings with lock-aware system-immediate transactions. The recovered overload uses `IClusterConnectionRecord` only for memory-backed stores that may need to connect to the cluster and determine whether the server can be removed safely.

## Dependencies and Integration Points
The declaration depends directly on `StorageServerInterface` and Flow actor types. The implementation integrates with worker recruitment and reboot logic, `IKeyValueStore` implementations, the log system, data distribution, ratekeeper, commit proxies, storage metrics, consistency scan, checkpoint and bulk dump subsystems, change feed streams, watch APIs, TSS pairing/quarantine, and system-key metadata helpers.

Worker call sites in `worker.actor.cpp` wrap the returned future with `handleIOErrors`, `storageServerRollbackRebooter`, and role error forwarding. `StorageServerInterface` is persisted in the database server list, so changes to interface behavior must be coordinated with client and management APIs. The storage server also reports queuing metrics, busy read tags, and storage state to ratekeeper and status collection.

## Risks and Edge Cases
The overloads take a raw `IKeyValueStore*`; ownership is managed by actor lifetime and termination code. A caller must not delete or reuse the store while the returned future is active. Error-code-specific cleanup is critical: disposing data on the wrong error could destroy recoverable storage, while closing when removal is final could leave stale files.

Recruitment and recovery have different interface-registration timing. New servers start accepting requests before `addStorageServer()` when no seed tag is provided, then durable metadata and recruiter reply follow; recovered servers first perform a non-accepting registration, then create a second registration future gated by `registerInterfaceAcceptingRequests`. Changes to this sequencing can affect availability, duplicate registration, and wrong-shard behavior.

TSS handling is intertwined with persistent identity. The new path sets the TSS pair before initialization, while recovery treats the persisted storage file as source of truth for TSS identity and updates the interface pair ID. Incorrect pair handling can cause a TSS to be registered as a normal storage server or rejoin the TSS map while quarantined.

The actor stack stores `StorageServer self` on the coroutine frame and passes `&self` to many child actors. The implementation cancels `storageServerCore`, halts locks, clears move-in shards, and waits a tick on termination to avoid dangling uses. Any new long-lived child actor must be added to the same lifetime discipline.

## Test Signals
Direct signals are build/link coverage for worker call sites and both overload signatures. Runtime signals include storage-server recruitment tests, worker reboot/recovery simulation, storage engine rollback tests, TSS simulation, memory-store recovery/removal behavior, and shard movement tests. Important traces include `StorageServerInitProgress`, `StorageServerInit`, `StorageServerRebootStart`, `SSTimeRestoreDurableState`, `StorageServerStartingCore`, `StorageServerTerminated`, `KVSRemoved`, and registration/tag traces such as `SSTag` and `SSHistory`.
