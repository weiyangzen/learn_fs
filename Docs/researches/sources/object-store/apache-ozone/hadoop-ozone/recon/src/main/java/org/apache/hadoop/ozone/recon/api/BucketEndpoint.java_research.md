# sources/object-store/apache-ozone/hadoop-ozone/recon/src/main/java/org/apache/hadoop/ozone/recon/api/BucketEndpoint.java

## Purpose
`BucketEndpoint` lists buckets known to Recon's OM metadata snapshot, optionally under a specific volume.

## Important APIs, Types, And Functions
The resource is `@Path("/buckets")`, JSON-producing, and `@AdminOnly`. `getBuckets(volume, limit, prevKey)` returns `BucketsResponse` containing `BucketObjectDBInfo` wrappers.

## Control Flow
The endpoint delegates to `ReconOMMetadataManager.listBucketsUnderVolume(volume, prevKey, limit)`, maps each `OmBucketInfo` into API metadata, counts the returned buckets, and returns a JSON response.

## State And Persistence
It reads the OM metadata snapshot through `ReconOMMetadataManager`. It has no local mutable state beyond the injected manager reference.

## Dependencies And Integration Points
It integrates REST query constants, OM metadata manager bucket listing, `OmBucketInfo`, and bucket response DTOs.

## Risks
No explicit validation is performed for negative limits or malformed volume names here; behavior depends on the metadata manager. The field is both `@Inject` annotated and constructor-injected, which is redundant.

## Test Signals
Tests should cover unscoped and volume-scoped listing, pagination via `prevKey`, limit handling, empty results, and IOException propagation.
