# sources/storage-engines/foundationdb/fdbclient/include/fdbclient/MonitorLeader.h

## Purpose
Declares client-side leader monitoring and proxy monitoring helpers. These functions discover the current cluster controller/coordinator leader, deserialize leader interfaces, collect client info, and keep proxy lists current for database clients.

## Important APIs, Types, And Functions
`CLUSTER_FILE_ENV_VAR_NAME` names the environment variable for cluster-file selection. `ClientStatusInfo` stores trace log group, supported client versions, and issues. `ClientData` stores client status by address plus an async variable for serialized `ClientDBInfo`; `getRequest()` builds an open-database request. `MonitorLeaderInfo` tracks connection progress and intermediate records. `getLeader()` elects a leader from nominee results. `monitorLeader()` is the templated public monitor; `monitorLeaderAndGetClientInfo()`, `monitorProxies()`, and `shrinkProxyList()` manage higher-level client info/proxy state. `LeaderDeserializer` defaults to `asyncDeserialize`, with a `ClusterInterface` specialization.

## Control Flow
`monitorLeader()` creates an `AsyncVar<Value>` for serialized leader info, starts `monitorLeaderInternal()` to refresh it, and races/combines it with a deserializer that updates the typed `outKnownLeader`. The election algorithm contacts coordinators, collects nominees, chooses the most nominated leader, and updates known leader state when stable. Proxy monitoring follows the leader-provided `ClientDBInfo` and prunes proxy lists when server UIDs change.

## State And Persistence Behavior
This header defines in-memory monitoring state only: async variables, maps of client status info, and last-known proxy UID/interface vectors. Persistent cluster coordination state is read from coordinators/connection records, not stored here.

## Dependencies And Integration Points
The header depends on client boolean params, FDB types, coordination interfaces, cluster interfaces, and commit proxy interfaces. It integrates with database open flow, client location/proxy selection, coordinator quorum, multiversion client status, and cluster file handling.

## Risks And Test Signals
Risks include leader election instability, stale serialized interface data, deserialization failures across protocol versions, proxy list churn, and incorrect client status aggregation. Test signals should include coordinator failover simulations, cluster-file changes, protocol/version compatibility tests, proxy shrink behavior, and client status output validation.
