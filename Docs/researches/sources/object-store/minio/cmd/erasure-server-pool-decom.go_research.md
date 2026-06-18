# sources/object-store/minio/cmd/erasure-server-pool-decom.go

## Purpose
This file implements erasure server pool decommissioning. It owns the persistent `pool.bin` state model, APIs for starting/canceling/failing/completing pool decommission, background migration of all bucket and metadata objects away from a suspended pool, status reporting, resume after restart, and trace/audit emission. It is tightly coupled to `erasureServerPools` in `erasure-server-pool.go` and reuses the same data movement safeguards used by rebalance.

## Important APIs, Types, and Functions
`PoolDecommissionInfo` is the persisted and admin-visible decommission progress structure. It records start/current/total size, terminal flags, queued and completed buckets, current bucket/object resume markers, and item/byte success/failure counters.

`PoolStatus` stores per-pool identity, command-line string, last update, and optional `PoolDecommissionInfo`. `poolMeta` wraps all `PoolStatus` entries, has the msgp generation marker, and persists to `pool.bin`.

Key `poolMeta` methods include `returnResumablePools`, `Decommission`, `DecommissionComplete`, `DecommissionFailed`, `DecommissionCancel`, `QueueBuckets`, `PendingBuckets`, `TrackCurrentBucketObject`, `CountItem`, `validate`, `load`, `save`, and `updateAfter`. These methods are the durable state machine for decommission.

Key `erasureServerPools` methods include `Init`, `IsDecommissionRunning`, `StartDecommission`, `Decommission`, `doDecommissionInRoutine`, `decommissionInBackground`, `decommissionPool`, `decommissionObject`, `checkAfterDecom`, `Status`, `ReloadPoolMeta`, `DecommissionCancel`, `DecommissionFailed`, and `CompleteDecommission`.

## Control Flow
Startup calls `Init`, which first loads rebalance metadata and starts rebalance if needed, then loads `pool.bin` from the first server pool, validates it against current command-line pools, writes a fresh merged `poolMeta` when pool membership changed, and resumes any non-terminal decommission after a 3 minute stabilization delay on the pool leader.

Starting decommission calls `StartDecommission`, which gathers all user buckets plus `.minio.sys/config` and `.minio.sys/buckets` metadata prefixes, heals metadata buckets, creates missing metadata bucket paths, marks selected pools as decommissioning, queues all buckets, persists `pool.bin` to all pools, and notifies peers to reload pool metadata. `Decommission` then launches serial background routines for the selected pool indices.

`doDecommissionInRoutine` creates a cancelable global context, calls `decommissionInBackground`, and marks the pool failed or complete. A successful pass is followed by `checkAfterDecom`, which scans the source pool to verify no non-ignored versions remain.

`decommissionPool` creates bounded workers, lists raw metadata from each set, sorts versions oldest first, applies lifecycle, preserves delete markers and remote/tiered objects, copies local object data, then deletes source object versions when all versions moved.

`decommissionObject` preserves multipart and single-part metadata. Multipart objects are re-created with `NewMultipartUpload`, per-part `PutObjectPart`, original ETags, index callbacks, and `CompleteMultipartUpload`. Single-part objects use `PutObject`. Both paths set `DataMovement` and `SrcPoolIdx` so the destination chooser refuses to write back to the source pool.

## State and Persistence Behavior
`pool.bin` has a 4 byte little-endian header: format and version, then msgp-encoded `poolMeta`. It is saved to every pool, not only the first one, so decommissioning the first pool remains possible.

`poolMeta.dontSave` suppresses writes before initial load is complete. `updateAfter` throttles progress persistence to at most once per duration, used with a 30 second interval in the object loop. Successful bucket completion and terminal status changes save immediately and notify peers.

The pool is considered suspended whenever its `PoolStatus.Decommission` is non-nil, regardless of terminal flags. This means normal write routing avoids the pool after decommission metadata exists and expects completed pools to be removed from the server command line.

## Dependencies and Integration Points
The file depends on bucket lifecycle, versioning, object lock retention, replication config, hash readers, MinIO audit/log/trace systems, raw metadata listing, peer notification reloads, admin pool handlers, and the core object APIs implemented in `erasure-server-pool.go`.

It integrates with `ObjectOptions` fields `DataMovement`, `SrcPoolIdx`, `SkipDecommissioned`, `Versioned`, `DeleteMarker`, `NoAuditLog`, `MTime`, `UserDefined`, and `IndexCB`. It uses `globalNotificationSys.ReloadPoolMeta` to fan out state changes.

## Risks and Test Signals
Pool suspension is driven by a non-nil decommission field, so cancellation or failure still leaves the pool treated as suspended unless state is otherwise cleared or the code path explicitly handles the terminal condition. Lifecycle, object lock, replication, remote-tier, multipart, and delete-marker handling are high-risk paths. The final `checkAfterDecom` scan is important because several concurrent-change errors are intentionally ignored during migration.

The direct handwritten test file validates `poolMeta.validate` across fresh setup, pool additions/removals, reordering, and decommission markers. Generated msgp tests cover zero-value codec round trips. There is no direct unit test here for full object migration, lifecycle filtering, remote-tier movement, cancel races, or final verification.
