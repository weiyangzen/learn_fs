# sources/storage-engines/foundationdb/fdbserver/core/include/fdbserver/core/ServerDBInfo.h

## Purpose
This header defines `ServerDBInfo`, the transient database metadata broadcast to workers so server roles can locate the cluster controller, master, proxies, resolvers, logs, ratekeeper, data distributor, consistency scan, and client-facing database info.

## Important APIs, Types, And Functions
`ServerDBInfo` stores an update `id`, `ClusterControllerFullInterface`, `ClientDBInfo`, optional distributor/ratekeeper/consistency-scan interfaces, `MasterInterface`, resolver list, recovery count/state, master lifetime, log system config, prior committed log servers, optional latency-band config, and info generation. `UpdateServerDBInfoRequest` carries serialized DB info and endpoint broadcast data; `GetServerDBInfoRequest` asks the controller for a newer value. `broadcastTxnRequest` and `broadcastDBInfoRequest` fan out updates.

## Control Flow
Cluster controller/master update `ServerDBInfo`, workers receive broadcasts through `WorkerInterface.updateServerDBInfo`, and stale workers can request the current value by known ID.

## State And Persistence Behavior
The object is transient and not client-visible, but it mirrors recovery/coordinated-state decisions. `myLocality` is explicitly not serialized.

## Dependencies And Integration Points
It depends on data distributor, consistency scan, latency bands, log system, master, ratekeeper, recovery, and worker interfaces. It is a central integration point for nearly all server roles.

## Risks And Edge Cases
Missing or stale `ServerDBInfo` causes workers to contact obsolete roles. Serialization changes have broad compatibility impact. `priorCommittedLogServers` must keep old logs alive while recovery is not fully committed.

## Test Signals
Signals include broadcast fanout counts, stale known-ID behavior, role replacement updates, recovery-state propagation, latency-band propagation, and correct omission of local-only data.
