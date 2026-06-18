# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/WorkerInterface.actor.h

## Purpose
This large header defines the worker and cluster-controller RPC contracts used to recruit every server role, register workers, broadcast database info, run diagnostics, execute snapshots, and support testing.

## Important APIs, Types, And Functions
`WorkerInterface` embeds `ClientWorkerInterface`, locality, recruitment streams for TLog/master/proxies/DD/ratekeeper/consistency scan/resolver/storage/log router/backup/range backup, diagnostic streams, waitFailure, exec/snapshot/disk-store streams, DB info updates, and `TesterInterface`. `WorkerDetails` adds process class and health flags. `ClusterControllerFullInterface` extends client cluster interface with recruitment, registration, worker list, DB info, health, TLog rejoin, backup done, coordinator changes, and encryption mode. Many request/reply structs define role recruitment and worker operations. `Role`, `startRole`, `endRole`, `traceRole`, `openDBOnServer`, DB locality helpers, and `ioTimeoutError`/`ioDegradedOrTimeoutError` are declared/defined.

## Control Flow
Workers initialize endpoints, register with the cluster controller, receive role initialization requests, return role interfaces, and handle DB info updates. Cluster controller recruits sets of workers based on configuration and process class, while roles use helper actors for timeout/degraded handling.

## State And Persistence Behavior
Most state is transient RPC/interface state. Requests carry recovery epochs, versions, log tags, encryption modes, storage types, worker health, and snapshot payloads that control durable role behavior. Serialization order is a wire contract.

## Dependencies And Integration Points
It depends on backup, DD, master, TLog, ratekeeper, consistency scan, resolver, storage, tester, log system, recovery state, client worker, and actorcompiler headers. It is the central role-recruitment integration point.

## Risks And Edge Cases
Endpoint initialization omissions, serialization reordering, stale cluster-controller generations, dropped init replies in simulation, worker health false positives, and timeout fault injection can destabilize recovery. `ioTimeoutError` adjusts simulation time before speedup and can inject faults for unreliable processes.

## Test Signals
Simulation should cover role recruitment for every role, worker registration updates, TLog rejoin, backup completion, encryption mode queries, snapshot/exec/disk-store requests, worker health reporting, and I/O timeout/degraded paths.
