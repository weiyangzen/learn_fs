# sources/object-store/minio/cmd/admin-handlers-pools.go

## Purpose
`admin-handlers-pools.go` implements admin APIs for erasure-server-pool lifecycle operations: decommission start/cancel/status/list and rebalance start/status/stop. These endpoints expose cluster topology operations that are only valid for distributed erasure deployments with multiple server pools.

## Important APIs, Types, And Functions
The file defines two package-level errors, `errRebalanceDecommissionAlreadyRunning` and `errDecommissionRebalanceAlreadyRunning`, to enforce mutual exclusion between rebalance and decommission operations.

Primary handlers are `StartDecommission`, `CancelDecommission`, `StatusPool`, `ListPools`, `RebalanceStart`, `RebalanceStatus`, and `RebalanceStop`. The helper `proxyDecommissionRequest` forwards decommission operations to the correct node when the selected endpoint is remote or overridden by `_MINIO_DECOM_ENDPOINT_HOST`.

The code relies on `validateAdminReq` with `policy.DecommissionAdminAction`, `policy.ServerInfoAdminAction`, or `policy.RebalanceAdminAction`. It type-asserts the object layer to `*erasureServerPools`, uses `globalEndpoints` for pool resolution and legacy topology checks, uses `globalProxyEndpoints` and `proxyRequestByNodeIndex` for routing, and calls methods such as `Decommission`, `DecommissionCancel`, `Status`, `IsDecommissionRunning`, `IsRebalanceStarted`, `initRebalanceMeta`, `StartRebalance`, and `saveRebalanceStats`.

## Control Flow
Decommission start validates that the server is initialized, rejects legacy endpoint style, requires a multi-pool `*erasureServerPools` backend, rejects if decommission or rebalance is already active, parses the path pool list either as numeric pool IDs or endpoint-set names, validates each pool index against `z.serverPools`, then either proxies to the owning endpoint or calls `z.Decommission(ctx, poolIndices...)`.

Cancel and status handlers perform similar legacy/backend/index validation for a single pool. Cancel proxies if needed, otherwise calls `DecommissionCancel`. Status calls `pools.Status` and JSON-encodes one `PoolStatus`. `ListPools` loops over all `globalEndpoints`, collects every pool status, and encodes the slice.

`RebalanceStart` is coordinated from the first node of the first pool to serialize concurrent start attempts. If this node is remote, it proxies to the matching proxy endpoint. It then rejects unsupported single-pool or non-erasure-pool backends, rejects running decommission or already-started rebalance, lists all buckets, initializes rebalance metadata with the bucket names, starts the local rebalance routine, returns the generated rebalance ID, and notifies peers to load rebalance metadata.

`RebalanceStatus` also proxies to the first pool's first node for a consistent view. It maps `errRebalanceNotStarted` and `errConfigNotFound` to `ErrAdminRebalanceNotStarted`, logs other status failures, and JSON-encodes the rebalance status. `RebalanceStop` stops rebalance through the notification system, returns no-content success, persists stopped stats, and asks peers to reload rebalance metadata.

## State And Persistence Behavior
Pool decommission and rebalance are persistent cluster operations. Decommission affects the erasure-server-pool state machine and object migration for selected pools. Rebalance initialization writes rebalance metadata, and `RebalanceStop` persists stopped state through `saveRebalanceStats`. Notification calls (`LoadRebalanceMeta`, `StopRebalance`) propagate changes across peer nodes.

The handlers intentionally centralize rebalance start/status on the first pool's first node so concurrent or distributed admin clients do not create divergent rebalance views. Decommission routing uses the selected pool's first endpoint, or `_MINIO_DECOM_ENDPOINT_HOST` when explicitly configured, to run the operation on an appropriate cluster node.

## Dependencies And Integration Points
Dependencies include MinIO mux route variables, environment lookup, policy action constants, global endpoint/proxy topology, admin error mapping, and erasure-pool implementation types. The handlers integrate directly with backend pool lifecycle code and the notification subsystem used to fan out rebalance state.

These APIs are not meaningful for filesystem, single-pool erasure, or legacy endpoint layouts and therefore return `ErrNotImplemented` in those modes.

## Risks And Test Signals
Operational risk is high because these APIs move data and affect cluster capacity. Important safeguards include legacy-topology rejection, backend type checks, multi-pool checks, pool-index validation, rebalance/decommission mutual exclusion, and coordinated proxy routing. A bug in pool lookup or proxy target selection could start work on the wrong pool or return inconsistent status.

No tests for this file are included in this work item. Likely test signals live in integration/admin suites that exercise decommission and rebalance in distributed erasure setups. Manual validation should include by-name and by-id pool addressing, remote first-node proxying, already-running errors, single-pool rejection, and rebalance metadata reload notifications.
