# sources/user-network-fs/nfs-ganesha/src/include/nfs_metrics.h

## Purpose

`nfs_metrics.h` declares the monitoring hooks for RPC-level, NFSv3 request, NFSv4 operation/compound, GSS drop, and Ganesha build/info metrics.

## Important APIs, Types, and Functions

`ganesha_info` is a gauge handle. APIs include `nfs_metrics__init`, `register_ganesha_info_metrics`, `nfs_metrics__rpc_received`, `nfs_metrics__rpc_completed`, `nfs_metrics__rpcs_in_flight`, `nfs_metrics__gss_request_dropped`, `nfs_metrics__nfs4_op_completed`, `nfs_metrics__nfs4_compound_completed`, `nfs_metrics__nfs3_request`, and `nfs_metrics__nfs4_request`.

## Control Flow

Metrics initialize during server startup. Dispatch increments received/in-flight/completed counters around each RPC. NFSv4 compound handling records per-op and compound statuses/latency. NFSv3/NFSv4 request functions emit dynamic metrics with proc/op, result/status, export ID, path, and client IP.

## State and Persistence Behavior

Metric handles and counters are process-local and exported to monitoring backends. They do not affect protocol state, but labels can expose paths/client IPs.

## Dependencies and Integration Points

It depends on `dynamic_metrics.h`, NFSv4.1, NFSv3, export IDs, and elapsed-time types. It integrates with dispatcher, protocol operations, QoS monitoring, GSS handling, and server info registration.

## Risks and Test Signals

Risks include high-cardinality path/client labels, negative in-flight gauges, inconsistent success/failure status classification, unregistered metrics, and overhead in hot paths. Tests should initialize metrics once, record NFSv3 and NFSv4 requests, verify label values/status buckets, check in-flight increments/decrements under errors, and confirm info metrics include server scope.
