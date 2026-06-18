# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/request/bucket/OMBucketCreateRequest.java

## Purpose

`OMBucketCreateRequest` handles `CreateBucket` requests. It validates bucket naming, ACLs, encryption, replication defaults, bucket links, bucket-count limits, quotas, default ACL inheritance, bucket layout compatibility, and metadata-table cache updates.

## Important APIs, Types, And Functions

- `preExecute(OzoneManager)` validates the requested bucket name, performs create ACL checks, enforces `ozone.om.max.bucket`, resolves bucket encryption key info via KMS, validates source volume/bucket link fields, rejects encryption on bucket links, validates default replication config, and stamps creation/modification time.
- `validateAndUpdateCache(OzoneManager, ExecutionContext)` is the state mutation path.
- `checkQuotaBytesValid(...)` ensures bucket space quota is compatible with volume quota and existing bucket quotas.
- `checkQuotaInNamespace(...)` checks volume namespace quota before consuming one namespace entry for the new bucket.
- `addDefaultAcls(...)` merges configured user defaults and inherited volume default ACLs.
- Request validators reject EC bucket defaults before EC finalization, handle bucket layout before finalization, and force old clients to create `LEGACY` buckets.

## Control Flow And State

Validation acquires a volume read lock and bucket write lock, checks volume existence and bucket absence, validates quota, assigns object ID from transaction index, sets update ID, inherits ACLs, increments volume used namespace, and writes both volume and bucket cache entries. The response is `OMBucketCreateResponse`, which later persists the cache mutations through the double buffer. Auditing happens after locks are released.

## Dependencies And Integration Points

This class integrates with `OMMetadataManager` volume and bucket tables, OM locks, `OMMetrics`, KMS/BekInfo resolution, default replication validation, bucket layout upgrade validators, `OmBucketInfo`, `OmVolumeArgs`, ACL utilities, and `OMBucketCreateResponse`.

## Risks And Test Signals

High-risk areas are quota accounting, default bucket layout behavior for old clients, source bucket link validation, EC pre-finalization rejection, and ACL inheritance when `ignoreClientACLs` is enabled. Tests should assert table cache entries, object/update IDs, volume namespace increments, EC metrics, FSO bucket metrics, audit behavior on preExecute ACL failures, and errors for duplicate buckets, missing volumes, invalid quotas, and too many buckets.
