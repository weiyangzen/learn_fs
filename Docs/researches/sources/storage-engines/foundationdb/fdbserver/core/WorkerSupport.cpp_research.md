# sources/storage-engines/foundationdb/fdbserver/core/WorkerSupport.cpp

## sources/storage-engines/foundationdb/fdbserver/core/WorkerSupport.cpp

Purpose: provides worker-side helpers for broadcasting database information, classifying addresses by database region, tracing worker roles, and registering static role descriptors.

Important APIs/types: explicit `RequestStream`/`NetNotifiedQueue` instantiations for master/proxy/db-info requests; `broadcastDBInfoRequest`, `broadcastTxnRequest`, `addressInDbAndPrimarySatelliteDc`, `addressInDbAndRemoteDc`, `startRole`, `endRole`, `traceRole`, and static `Role` constants.

Control flow and state: broadcast helpers partition `broadcastInfo` endpoints over `sendAmount` streams, reset reply promises between sends, wait for all replies, and optionally reply to the original requester. DB-info broadcast returns endpoints that were not updated, including sender when provided and failed sub-broadcasts from `tryDBInfoBroadcast`. Address helpers scan current `ServerDBInfo` log sets, remote log routers, and optional storage server address lists. Role lifecycle helpers update trace roles, emit begin/end/refresh trace events, maintain process-global `g_roles`, update `StringMetricHandle` values, manipulate latest event cache, and notify the simulator role map.

Dependencies and integration: depends on simulator, `ServerDBInfo`, Flow trace/metrics/generic actors, network addresses, log system locality tags, and worker role definitions. It integrates with cluster controller recruitment, status role reporting, transaction state propagation, and simulation visualization.

Risks and tests: broadcast partitioning must preserve all endpoints and not reuse stale reply promises. Global `g_roles` is process-local mutable state and must stay balanced across start/end paths. Tests should cover partial broadcast failure, sender exclusion, remote/satellite address classification, role metrics updates, and simulated add/remove role calls.
