# sources/storage-engines/foundationdb/fdbclient/StatusClient.cpp

## Purpose
`StatusClient.cpp` implements client-side status collection and JSON status document merging for FoundationDB. It has two major responsibilities: strict parsing/merging/cleanup of JSON status fragments through `JSONDoc`, and asynchronous status fetching from coordinators plus the cluster controller through `StatusClient::statusFetcher`.

## Important APIs, types, and functions
`readJSONStrictly()` parses a complete JSON string with `json_spirit`, allowing only trailing whitespace and throwing `json_malformed` or `json_eof_expected` on malformed input. `JSONDoc::mergeValueInto()`, `mergeInto()`, `cleanOps()`, and `mergeOperator` specializations implement status-document operators such as `$and`, `$or`, `$count_keys`, `$latest`, `$last`, and `$expires`. `clientCoordinatorsStatusFetcher()` probes coordinator leader and protocol endpoints and reports quorum reachability. `clientStatusFetcher()` builds the client section, including cluster-file freshness. `clusterStatusFetcher()` requests the selected status field from the cluster controller. `getClientDatabaseStatus()` derives `healthy` and `available` booleans from client and cluster status JSON. `statusFetcherImpl()` orchestrates deadlines and merges client/cluster output. `timeoutMonitorLeader()` keeps `monitorLeader` active only while status is being requested. `StatusClient::statusFetcher()` is the public entry point.

## Control flow
Status collection first computes a deadline using `CLIENT_KNOBS->STATUS_TIMEOUT`, probes coordinators, and checks whether the cluster file is current. If quorum is reachable, it waits briefly for `db->statusClusterInterface` to be populated by `monitorLeader`, then asks `databaseStatus` on the cluster controller. Messages are accumulated instead of generally throwing so partially complete status is still returned. Once cluster data is present, coordinator fault tolerance is folded into the cluster fault tolerance section. The final document always gets `client.messages`, `client.database_status`, and a default `cluster.layers._valid` field.

## State and persistence behavior
This file does not persist database keys directly. It reads cluster connection state from `IClusterConnectionRecord` and caches status leader monitoring state in `DatabaseContext` fields `statusClusterInterface`, `statusLeaderMon`, and `lastStatusFetch`. `JSONDoc::expires_reference_version` is a process-static version threshold used when resolving `$expires` operators.

## Dependencies and integration points
It integrates with `CoordinationInterface`, `MonitorLeader`, `ClusterInterface`, `Status`, generic RPC retry helpers, `json_spirit`, Flow coroutines, and client knobs. The status output feeds CLI and management status consumers, and its message types must stay consistent with `fdbclient/Status.h`.

## Risks and edge cases
JSON merging is type-sensitive: mismatched scalar values or operators produce embedded `ERROR` objects rather than exceptions. `$expires` behavior depends on `expires_reference_version`, and a missing or zero version is treated as unexpired. Coordinator probing races a quorum wait against timeout delay; partial readiness can produce incomplete but valid status. Health derivation is intentionally conservative and catches JSON access exceptions by leaving availability or health false. The idle monitor resets the cached cluster interface after `STATUS_IDLE_TIMEOUT`, so callers must tolerate re-monitoring cost after idle periods.

## Test signals
There are no local `TEST_CASE`s in this file. Useful test signals are simulation malformed JSON checks, status command tests with unavailable coordinators or cluster controller, cluster-file mismatch tests, JSON operator merge tests, and status timeout behavior. Trace events `ClientStatusFetchError` and `ClusterStatusFetchError` are operational diagnostics.
