# sources/object-store/minio/cmd/erasure-server-pool.go

## Purpose
This file implements MinIO's multi-pool erasure object layer. It initializes erasure pools, chooses destination pools, routes object and multipart operations, merges listings and scans, handles bucket operations, health and storage info, healing, metadata/tag/tier operations, and delegates decommission and rebalance state checks.

## Important APIs, Types, and Functions
`erasureServerPools` is the central object-layer type. It contains `poolMeta` guarded by `poolMetaMutex`, `rebalanceMeta` guarded by `rebalMu`, deployment identity, distribution algorithm, `serverPools`, decommission cancelers, `S3PeerSys`, and multipart upload cache.

Initialization is handled by `newErasureServerPools`, which validates parity and deployment IDs, waits for erasure formats, creates `erasureSets`, initializes byte pools, global locks, auto-heal, pool metadata, and stale multipart cleanup.

Pool selection and lookup are handled by `getServerPoolsAvailableSpace`, `getAvailablePoolIdx`, `getPoolInfoExistingWithOpts`, `poolsWithObject`, `getPoolIdxExistingWithOpts`, `getPoolIdxNoLock`, and `getPoolIdx`.

Object APIs include `GetObjectNInfo`, `GetObjectInfo`, `PutObject`, `DeleteObject`, `DeleteObjects`, `CopyObject`, listing variants, multipart lifecycle methods, metadata/tag methods, transition/restore, and `DecomTieredObject`. Operational APIs include `NSScanner`, `Walk`, `HealObjects`, `HealObject`, `Health`, `StorageInfo`, `BackendInfo`, `GetRawData`, and disk lookup helpers.

## Control Flow
Initialization builds all pools from endpoint server pools, enforces consistent deployment ID, populates local-drive maps for non-distributed erasure, creates `poolMeta` with `dontSave`, then repeatedly calls `Init` until backend metadata loads or a non-retriable error occurs. It then initializes the multipart cache and starts a cleanup goroutine.

Writes first try to find an existing object's pool. For new data, `getAvailablePoolIdx` computes weighted available capacity across non-suspended and non-rebalancing pools and randomly chooses a pool proportional to available bytes. Pools above the reserve threshold can be filtered out unless all pools exceed it.

Reads query all pools in multi-pool mode and choose the latest object by modification time, with lowest pool index as a tie-break. Deletes acquire namespace locks, identify the pool with the latest object, handle delete-marker special cases, optionally delete across all pools with no/read-quorum metadata inconsistencies, and route replication or data movement requests to the correct pool.

Multipart operations preserve upload affinity by searching existing uploads across active pools before creating new uploads. Listing and walking merge raw metadata streams across pools and sets, with several client-specific fast paths.

## State and Persistence Behavior
The file itself owns in-memory coordination state: `poolMeta`, `rebalMeta`, decommission cancelers, rebalance canceler, byte pool cap, local drive map, global object layer assignment, and multipart cache. Durable decommission and rebalance persistence is implemented in the companion files through `pool.bin` and `rebalance.bin`.

`poolMeta` and `rebalMeta` are read on routing paths to avoid suspended or rebalancing pools. This makes persisted admin state directly affect normal S3 operation routing. Multipart cache entries are local hints and are removed after configurable stale-upload expiry or when uploads complete/abort.

## Dependencies, Risks, and Test Signals
The file integrates with storage class parity, endpoint formats, erasure sets, global notification system, bucket metadata, lifecycle evaluation, object lock, tags, namespace locks, S3 peer system, healing, scanner, metrics, admin health endpoints, and decommission/rebalance companion files.

Multi-pool object lookup is defensive against duplicate objects and serves the latest `ModTime`; this hides some split-brain states but makes ordering important. Routing avoids suspended and rebalancing pools for new writes and fails disk-full if none can accept data. Data movement relies on `DataMovement` plus `SrcPoolIdx` to prevent copying back to the same pool.

`CheckAbandonedParts` appears to return inside the first iteration over `errs`, which means it returns the first error value, including nil, without scanning later errors. That is a risk signal worth review. The listed tests do not directly cover this large file except through erasure pool setup in `erasure-server-pool-decom_test.go`.
