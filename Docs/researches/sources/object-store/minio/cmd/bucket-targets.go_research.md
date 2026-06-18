# sources/object-store/minio/cmd/bucket-targets.go

## Purpose
This file implements MinIO's in-memory bucket remote target subsystem. It stores bucket-to-target configuration, constructs minio-go clients, validates target reachability and versioning, tracks endpoint health and latency, manages bandwidth limits, and supplies target clients to replication code.

## Important APIs, types, and functions
`BucketTargetSys` owns `arnRemotesMap`, `targetsMap`, health-check state, an anonymous health client, and ARN reload/error tracking. `TargetClient` embeds `*minio.Client` and stores target bucket, storage class, sync replication mode, proxy-disable flag, ARN, reset ID, endpoint, and secure flag. Key methods include `NewBucketTargetSys`, `SetTarget`, `RemoveTarget`, `UpdateAllTargets`, `set`, `ListTargets`, `ListBucketTargets`, `GetRemoteTargetClient`, `GetRemoteBucketTargetByArn`, `getRemoteTargetClient`, `getRemoteARN`, `getRemoteARNForPeer`, `generateARN`, and `parseBucketTargetConfig`.

## Control flow
Targets are loaded from metadata through `set`/`UpdateAllTargets`, which build clients and update bandwidth throttles. Admin additions use `SetTarget`: validate type, create a client, confirm bucket existence/access, require source and target versioning for replication targets, perform a short liveness probe, reject duplicate targets, update maps, and apply throttles. `GetRemoteTargetClient` returns cached clients and may trigger lazy metadata refresh when a client is missing. Heartbeat goroutines periodically call anonymous `Alive`, compute online state, downtime, and latency, and rebuild the health map to remove stale endpoints.

## State and persistence behavior
State is in-memory and protected by locks. Persistent target configuration lives in bucket metadata and is parsed by `parseBucketTargetConfig`, including optional decryption for encrypted metadata. Bandwidth limits are applied to `globalBucketMonitor` from persisted target config.

## Dependencies and integration points
The subsystem integrates with `madmin.BucketTarget(s)`, minio-go clients/credentials, `globalRemoteTargetTransport`, `globalBucketVersioningSys`, `globalBucketMetadataSys`, `globalBucketMonitor`, KMS-backed metadata decryption, replication config removal checks, and site replication peer lookup. `bucket-replication.go` depends on `TargetClient` lookup, offline checks, sync flags, storage class, proxy settings, reset IDs, and target buckets.

## Risks and test signals
Health defaults missing endpoints to online and initializes asynchronously, briefly allowing work to an unproven endpoint. Multiple mutexes protect related maps, so changes must respect lock boundaries. Lazy refresh and `markRefreshInProgress` deserve careful testing. Target credentials and decrypted config are sensitive. No direct tests are included in this subset; expected coverage is indirect through admin target APIs and replication workflows.
