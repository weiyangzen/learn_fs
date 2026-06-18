# sources/object-store/minio/cmd/bucket-versioning-handler.go

## Purpose
This file implements the S3-compatible HTTP handlers for PUT and GET Bucket Versioning. It parses and validates versioning XML, enforces constraints from site replication, object lock, and bucket replication, persists bucket versioning config, triggers site-replication metadata hooks, and returns the current config.

## Important APIs, types, and functions
`bucketVersioningConfig` names the persisted metadata object (`versioning.xml`). `maxBucketVersioningConfigSize` caps request XML at 1 MiB. `objectAPIHandlers.PutBucketVersioningHandler` handles writes, and `objectAPIHandlers.GetBucketVersioningHandler` handles reads.

## Control flow
PUT creates request context and audit logging, extracts the bucket, checks object-layer initialization, authorizes `policy.PutBucketVersioningAction`, parses XML through `versioning.ParseConfig(io.LimitReader(...))`, and enforces state constraints: site replication cannot coexist with disabled versioning, object-lock buckets cannot suspend versioning or exclude prefixes, and buckets with replication config cannot suspend bucket-wide versioning. It marshals XML, persists through `globalBucketMetadataSys.Update`, base64-encodes the XML for `globalSiteReplicationSys.BucketMetaHook`, logs hook errors, and returns success. GET authorizes, verifies bucket existence, loads config through `globalBucketVersioningSys.Get`, marshals XML, and writes the response.

## State and persistence behavior
PUT persists versioning XML under `versioning.xml` in bucket metadata and propagates the update timestamp into the site replication hook. GET is read-only. Versioning state affects object write/delete semantics, replication eligibility, object-lock legality, and prefix-exclusion behavior elsewhere.

## Dependencies and integration points
The handlers integrate with the object layer, bucket metadata system, `versioning` parser, auth/policy checks, object-lock config, `getReplicationConfig`, `globalSiteReplicationSys`, audit logging, mux routing, API error conversion, and XML helpers. The constraints protect assumptions used by replication and object-lock code.

## Risks and test signals
Constraint ordering affects returned API errors. Prefix exclusions are a MinIO extension and are forbidden with object lock because they can effectively suspend versioning for a prefix. Site replication hook failure does not roll back local persistence. No direct tests are included here; useful coverage includes malformed XML, oversized bodies, object-lock exclusions, replication-config suspension rejection, and site hook behavior.
