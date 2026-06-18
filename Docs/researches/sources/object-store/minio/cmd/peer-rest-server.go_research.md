# sources/object-store/minio/cmd/peer-rest-server.go

## Purpose
This file implements and registers the server side of MinIO peer REST/grid APIs. It exposes local node state and mutating admin operations to authenticated peers in distributed deployments.

## Important APIs, Types, and Functions
`peerRESTServer` is the handler receiver. The large `var` block defines pooled grid JSON/array wrappers and typed grid handlers for IAM, bucket metadata, stats, metrics, metacache, S3 bucket operations, rebalance, service signals, and streams. Handler methods include IAM delete/load operations, profiling, storage/server/system info, metric collection, bucket metadata reload/delete, listen/trace/console streaming, binary verify/commit, speed tests, netperf, replication MRF, heal/list/head/make/delete bucket, and `registerPeerRESTHandlers`.

## Control Flow and State
Most grid handlers validate object layer availability, parse `grid.MSS` parameters, call a global subsystem, and return `grid.RemoteErr` on failure. Legacy HTTP handlers authenticate through `IsValid`, use gob or zstd when needed, and drain/encode response bodies. Service signals can sleep until a scheduled time and may write to `globalServiceSignalCh`.

## Dependencies and Integration Points
The file integrates with global IAM, bucket metadata, event notifier, replication stats, grid manager, lock server, profiler, object layer, rebalance pools, tier config, metrics registries, console system, and router setup.

## Risks and Test Signals
This is a high-blast-radius internode surface: handlers mutate IAM caches, bucket metadata, binary state, rebalance state, and service lifecycle. Parameter validation is uneven across handlers, and some reloads run asynchronously or best-effort. Streaming handlers must handle slow clients without blocking publishers. Coverage is mostly integration-level through admin, peer, and bucket tests rather than direct unit tests in this subset.
