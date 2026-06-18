# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/OzoneManagerUtils.java

## Purpose
`OzoneManagerUtils` provides small static helpers for OM request handling, especially bucket lookup/layout resolution through bucket links and delegation-token audit map construction.

## Important APIs, types, and functions
- `getBucketInfo(OMMetadataManager, volName, buckName)` reads the bucket table and reports precise volume-not-found or bucket-not-found exceptions.
- `getBucketLayout(...)` returns the resolved bucket layout after following link buckets.
- `getResolvedBucketInfo(...)` follows bucket links and returns the final source bucket information.
- `resolveBucketInfoLink(...)` is the recursive implementation with visited-set loop detection.
- `buildTokenAuditMap(Token<OzoneTokenIdentifier>)` extracts token kind and service into a linked audit map.

## Control flow
Bucket resolution reads the requested bucket. If it is not a link, it returns immediately. If it is a link, it adds the current volume/bucket pair to a visited set, fails on repeats, and recurses to the source volume/bucket until a non-link bucket is found. Missing bucket resolution first checks whether the volume exists so the caller receives a more specific result code.

## State and persistence behavior
The utility is stateless and performs no writes. It reads OM metadata tables through `OMMetadataManager`; audit-map construction reads token metadata only.

## Dependencies and integration points
The class is used in the OM write request path, as noted by the in-file call trace from `OzoneManagerStateMachine#applyTransaction` through request factories to bucket layout resolution. It depends on `OMMetadataManager`, `OmBucketInfo`, `BucketLayout`, Apache Commons `Pair`, `OMException`, and token/audit constants.

## Risks and edge cases
Deep link chains recurse and could be expensive or stack-heavy if misconfigured. Link cycles are detected only by exact volume/bucket pairs. Dangling links surface as bucket or volume not found. The utility does not perform ACL checks; callers that expose client-visible operations must enforce authorization separately.

## Test signals
Tests should cover direct bucket layout, chained links, link loop detection, dangling source bucket, missing source volume, missing requested bucket with existing volume, missing volume, and null token kind/service values in audit-map construction.
