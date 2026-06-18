# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketSetPropertyRequest.java

## Purpose

`OMBucketSetPropertyRequest` updates mutable bucket properties: metadata, storage type, versioning, byte and namespace quotas, default replication config, and encryption key info. It deliberately rejects property updates on bucket links.

## Important APIs, Types, And Functions

- `preExecute(OzoneManager)` stamps modification time and resolves bucket encryption key info through the KMS provider when requested.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` performs authorization, loads bucket/volume state, applies requested fields to an `OmBucketInfo.Builder`, validates quotas, and writes a bucket cache update.
- `checkAclPermission(...)` uses native admin/owner semantics for native ACLs and `WRITE` ACL for Ranger/external authorizers.
- `checkQuotaBytesValid(...)` and `checkQuotaNamespaceValid(...)` enforce reset rules and prevent setting quotas below existing usage.
- `disallowSetBucketPropertyWithECReplicationConfig(...)` rejects EC defaults before EC finalization.

## Control Flow And State

The request increments bucket-update metrics, resolves `OmBucketArgs`, acquires the bucket write lock, rejects missing buckets and links, merges metadata, updates modification/update IDs, conditionally updates storage type/versioning/quotas/default replication/encryption, and writes the new `OmBucketInfo` to the bucket table cache. It reads volume state for quota validation but does not mutate volume state. Audit logging is outside the lock.

## Dependencies And Integration Points

The class integrates with KMS/BekInfo, `OMMetadataManager` bucket and volume tables, quota constants, `DefaultReplicationConfig`, native and external ACL authorizers, `OMBucketSetPropertyResponse`, and upgrade validation.

## Risks And Test Signals

Risks include quota reset semantics when volume quota is still set, quota reductions below used bytes/namespace, metadata overwrite/merge behavior, encryption key resolution, and ACL differences between native and Ranger paths. Tests should cover link rejection, EC pre-finalization rejection, all optional property fields, volume quota aggregation across buckets, successful cache update IDs, and failure metric increments.
