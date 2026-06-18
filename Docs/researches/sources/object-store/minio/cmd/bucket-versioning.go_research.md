# sources/object-store/minio/cmd/bucket-versioning.go

## Purpose
This file defines the lightweight bucket versioning subsystem wrapper. It centralizes reads of bucket versioning configuration and exposes convenience predicates used by object, delete, replication, target validation, and handler paths.

## Important APIs, types, and functions
`BucketVersioningSys` is stateless. `Enabled`, `Suspended`, `PrefixEnabled`, and `PrefixSuspended` call `Get` and delegate to `versioning.Versioning` methods. `Get` reads versioning config from `globalBucketMetadataSys.GetVersioningConfig`, except for `minioMetaBucket` and names with that prefix, where it returns a default XMLNS config. `NewBucketVersioningSys` returns a new wrapper.

## Control flow
All predicates load config on demand. If `Get` returns an error, they log with `logger.CriticalIf(GlobalContext, err)` and then call the method on the returned config. The metadata bucket special case keeps internal metadata operations independent of ordinary bucket versioning settings.

## State and persistence behavior
The wrapper stores no state and does not cache. Persistence lives in bucket metadata, written by the versioning handler and read through the metadata system. Prefix-aware versioning is a MinIO extension represented in `versioning.Versioning`.

## Dependencies and integration points
`bucket-replication.go` uses prefix enablement/suspension to skip replication for excluded prefixes and set delete options. `bucket-targets.go` uses `Enabled` to validate replication source buckets. The HTTP handler uses `Get` for GET Bucket Versioning.

## Risks and test signals
Predicate methods rely on `GetVersioningConfig` returning a non-nil config even when logging an error; otherwise they could panic. The metadata-bucket prefix check must not collide unexpectedly with user bucket names. Lack of caching keeps reads fresh but may make hot paths depend on metadata-system performance. No direct tests are included in this subset.
