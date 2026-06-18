# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManager.java

## Purpose
`OzoneManager` is the central server implementation for Apache Ozone Manager. It owns OM startup, storage validation, RPC/gRPC/HTTP endpoints, HA Ratis integration, metadata manager lifecycle, security token services, ACL and admin authorization helpers, S3 multi-tenancy routing, snapshot reads and diffs, prepare-state recovery, metrics, and many read-side methods from `OzoneManagerProtocol`, `OMInterServiceProtocol`, admin, auditor, and runtime-info interfaces.

## Important APIs, types, and functions
- `createOm`, `omInit`, `initializeSecurity`, and `StartupOption` construct, initialize, bootstrap, or securely enroll an OM.
- The constructor loads HA node details, validates `OMStorage`, checks SCM cluster identity, configures default bucket layout and replication, creates SCM clients, security clients, metrics, managers, Ratis directories, Ratis server, RPC translators, optional S3G gRPC server, and the request execution flow.
- `instantiateServices(boolean)` rebuilds all DB-dependent services: `OmMetadataManagerImpl`, volume/bucket/key/prefix managers, multi-tenancy manager, S3 secret manager, authorizer, active metadata reader, snapshot manager, snapshot metrics, and prepare state.
- `start`, `restart`, `stop`, `close`, `join`, `terminateOM`, and `shutDown` control runtime lifecycle.
- RPC setup is split across `getRpcServer`, `startRpcServer`, and `startGrpcServer`, registering client, inter-OM, admin, and reconfiguration protobuf services.
- Protocol methods include volume/bucket/key listing and lookup, file status/listing, ACL reads, delegation token operations, service discovery, open-file listing, leadership transfer, Ranger sync trigger, snapshot defrag trigger, tenant listing/user lookup, S3 volume resolution, multipart listing, DB update streaming, safe-mode proxying to SCM, quota repair, object tagging, snapshot diff APIs, and OM DB compaction.
- HA and Ratis helpers include `initializeRatisDirs`, `initializeRatisServer`, `bootstrap`, `updatePeerList`, `addOMNodeToPeers`, `removeOMNodeFromPeers`, `isLeaderReady`, `checkLeaderStatus`, `installSnapshotFromLeader`, `installCheckpoint`, and checkpoint replacement helpers.
- Authorization helpers include `checkAcls`, `getAclsEnabled`, `isAdminAuthorizationEnabled`, `checkAdminUserPrivilege`, owner lookup helpers, admin/blacklist accessors, and `resolveBucketLink` variants.

## Control flow
Construction first freezes configuration-derived identity and storage state, then validates OM initialization and SCM cluster matching before creating network endpoints. Security setup happens before service discovery and token managers; DB-dependent managers are created by `instantiateServices(false)` before the S3 gateway volume is ensured in the DB. Ratis directories and server are prepared before RPC translators are built, because the translators submit write requests through Ratis.

`start()` initializes metrics, starts metadata storage, conditionally starts secret managers, starts Ratis, seeds metrics from DB and the saved metrics file, starts topology, key manager, HTTP server, RPC server, trash emptier, optional gRPC server, and JMX, then bootstraps if requested and moves `omState` to `RUNNING`. `restart()` repeats most initialization after reloading selected config and services. `stop()` reverses the order: mark stopped, close reconfiguration and timers, stop RPC/gRPC/Ratis/key/security/topology/HTTP/multi-tenant/trash/metadata/snapshot/metrics/service resources, close SCM and certificates, unregister metrics, and shut down the EDEK cache loader.

Read operations generally wrap manager calls with ACL checks, metrics increments, and audit success/failure logging. Key and filesystem reads call `getReader(...)`, which may return the active metadata reader or a snapshot metadata reader from `OmSnapshotManager`. Bucket-link resolution recursively follows link buckets with loop detection and optional ACL checks before dispatching to the real bucket.

Snapshot installation is a coordinated state transition: download a DB checkpoint from the leader, stop background services, invalidate snapshot cache, pause the Ratis state machine, compare checkpoint transaction info to the local last-applied index, stop RPC and metadata if the checkpoint is newer, selectively back up and replace DB directory entries using a transient marker, instantiate services against the new DB, unpause the state machine at the checkpoint term/index, restart RPC, audit the install, and delete the backup.

Prepare-state recovery occurs after metadata manager creation. On normal startup, OM compares a Ratis-replicated DB prepare marker with the local marker file, preferring the DB marker if both exist but differ, removing the DB marker when the local upgrade/downgrade startup flow removed the file, and failing startup if the file exists without a DB marker. After snapshot install, it restores or cancels prepare state from the snapshot DB marker.

## State and persistence behavior
Persistent state spans the OM VERSION file (`OMStorage`), RocksDB metadata tables, Ratis log/snapshot directories, prepare marker file under the OM current metadata directory, saved metrics JSON in the OM DB metadata directory, certificate serial IDs in storage, and transient DB backup/marker directories during checkpoint replacement. `addS3GVolumeToDB()` writes the default S3 volume and user entry directly to the DB and cache using a reserved transaction/object ID. `updateLayoutVersionInDB()` persists finalized metadata layout version in the meta table. `saveNewCertId()` persists certificate ID back to the VERSION file and shuts down on persistence failure.

In-memory state includes managers, authorizer, service provider, token managers, Ratis server, peer map, current transaction info, metrics, thread-local S3 authentication, booleans for RPC/gRPC running, feature flags, bucket layout and replication defaults, and `omState`. Several test flags alter reload, security, UGI, and snapshot-install behavior.

## Dependencies and integration points
This class is a hub for HDDS/Ozone subsystems: SCM clients and topology, Ratis, protobuf RPC translators, gRPC S3 gateway server, HTTP servlets, RocksDB metadata manager, KMS and EDEK warmup, delegation/block token security, certificate enrollment, S3 secret storage, Ozone native or Ranger authorizer, snapshot manager and defrag services, directory/key deleting services, multi-tenancy/Ranger sync, upgrade finalizer, reconfiguration, metrics/JMX, Hadoop `Trash`, and audit logging. External clients reach it through protobuf RPC, gRPC for S3 gateway OM requests, HTTP endpoints, and admin/reconfigure protocols.

## Risks and edge cases
- The class has a very large responsibility surface; changes to lifecycle order can break Ratis, metadata, security, or RPC availability.
- `StartupOption.REGUALR` is misspelled but part of the local API.
- Checkpoint installation is high risk: failed DB movement can force process exit if rollback cannot restore the previous state, and it intentionally stops RPC/metadata while moving files.
- Prepare-state divergence is guarded by DB/file marker reconciliation, but marker-file-only state is treated as corruption.
- `isLeaderReady()` returns true only when `omRatisServer` is non-null and ready, despite the comment saying non-Ratis always returns true.
- Some protocol methods are placeholders (`echoRPCReq`, `recoverLease`, `setTimes`) and return null or no-op.
- Bucket-link resolution must avoid loops and must use source-bucket ACL semantics before snapshot/key operations.
- S3 multi-tenancy routing depends on thread-local `S3_AUTH`; old gateways without S3 auth fall back to the default S3 volume.
- HTTP server startup failure is logged but non-fatal, so monitoring must detect missing web endpoints separately.
- Several operations rely on `getRemoteUser()` and `Server.getRemoteIp()` context; gRPC bridges must synthesize enough Hadoop RPC call context.

## Test signals
Useful tests include OM init with initialized/uninitialized storage, SCM cluster ID mismatch, secure startup without cert serial, default bucket layout validation before/after layout finalization, start/stop/restart resource ordering, RPC/gRPC endpoint enablement, HTTP failure tolerance, S3 volume auto-creation and cache updates, delegation token auth-method checks, admin authorization on leadership/repair/compaction APIs, bucket-link loop/dangling/ACL cases, prepare DB/file marker reconciliation across restart and snapshot install, checkpoint install success/rollback/failure paths, service list role/port construction, snapshot-reader routing for key/status/list/ACL/diff operations, and gRPC bridge behavior that depends on Hadoop `Server.Call` context.
