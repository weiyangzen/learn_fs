# sources/storage-engines/foundationdb/fdbserver/worker/worker.actor.cpp

## Purpose
`worker.actor.cpp` is the main `fdbd` worker-process orchestration file. It discovers persisted worker-local state, starts process services, registers the worker with the cluster controller, restores durable storage/TLog roles, accepts role recruitment requests, monitors health and local issues, and maps role actor failures into process reboot or shutdown behavior.

## Important APIs, Types, and Functions
- `fdbd(...)`: process entry actor. Starts protocol/process endpoints, optional coordination server, data/spill `processId` locks, software-version compatibility checks, CC leadership/candidacy, cluster-interface extraction, and `workerServer`.
- `workerServer(...)`: owns a `WorkerInterface`, restores disk roles, starts background monitors, registers with the cluster controller, and handles all role recruitment streams.
- `registrationClient(...)`: repeatedly sends `RegisterWorkerRequest` with process class, priority, optional role interfaces, degraded state, issues, recovered-disk status, incompatible peers, and cluster id.
- `forwardError`, `workerHandleErrors`, `handleIOErrors`, and `checkIOTimeout`: central error normalization and reboot policy.
- Disk naming/recovery helpers: `TLogOptions`, `DiskStore`, `filenameFromSample`, `filenameFromId`, `getDiskStores`.
- Health helpers: `addressInDbAndPrimaryDc`, `addressesInDbAndRemoteDc`, `addressIsRemoteLogRouter`, `doPeerHealthCheck`, `getStorageServers`, `healthMonitor`.
- Persistence helpers: `createAndLockProcessIdFile`, `createClusterIdFile`, `updateClusterId`, `testAndUpdateSoftwareVersionCompatibility`, `monitorAndWriteCCPriorityInfo`.

## Control Flow
`fdbd` starts base services, locks the data and TLog spill folders with a stable process id, validates/writes `sw-version`, then starts or monitors the cluster controller depending on process class. It launches `workerServer` and waits for one core actor to terminate.

`workerServer` initializes interface endpoints and background actors, scans data/spill folders, and restores storage servers and shared TLogs from disk before advertising stateful readiness. Its main `choose` loop handles DB info broadcasts, reboot/failure/profiler requests, and recruitment for master, data distributor, ratekeeper, consistency scan, backup, range backup, TLog, storage, commit proxy, GRV proxy, resolver, and log router. Each role is started with role-lineage tracing, endpoint token dumps, actor error forwarding, and a reply containing the recruited interface.

## State and Persistence Behavior
Persistent state includes storage-engine files/directories, TLog KV stores, TLog disk queues, `processId`, `clusterId`, `fitness`, `sw-version`, and `_validate`. Storage and TLog filenames encode component, UID, engine, and sometimes TLog options. `processId` is opened with `OPEN_LOCK`; a separate spill folder must contain the same process id. `clusterId` is created from DB info and later guards against joining the wrong cluster. `_validate` triggers data validation on checked reboot. In-memory state includes running storage IDs, storage cleanup actors, shared TLog slots, AsyncVars for role interfaces/issues/degraded state, and recovery promises.

## Dependencies and Integration Points
This file integrates almost every server subsystem: cluster controller, master, commit/GRV proxies, resolvers, TLogs, storage server, data distributor, ratekeeper, consistency scan, log router, backup workers, coordinator, tester, metrics logger, storage engines, disk queues, Flow transport, failure monitor, simulator, gRPC control service, and profiler/system monitor.

## Risks
Error classification is process-critical: misclassifying IO errors, timeouts, or `please_reboot*` can hide real corruption or cause churn. Disk filename parsing is a recovery boundary for every storage engine and TLog version. TLog spill folders reject duplicate TLog IDs and non-TLog stores. Health-monitor locality classification can create false gray-failure reports if DB info is stale or topology parsing changes. Actor lifetime ordering around `filesClosed`, reboot promises, and `sharedLogs` is subtle.

## Test Signals
Embedded `TEST_CASE`s cover address classification, remote log-router identification, software-version file compatibility/update behavior, and storage-engine clearing of in-flight commits. Runtime trace signals include `WorkerRegister`, `DiskFileRecoveriesComplete`, `WorkerHealthMonitor`, `StorageServerInitProgress`, `WorkerShutdownComplete`, and `StartingFDBD`.
