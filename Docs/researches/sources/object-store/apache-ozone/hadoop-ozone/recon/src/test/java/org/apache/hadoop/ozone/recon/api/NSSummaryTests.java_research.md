# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/api/NSSummaryTests.java

## Purpose
This abstract class contains shared namespace-summary endpoint assertions used by layout-specific `NSSummaryEndpoint` tests. It verifies basic-info responses for root, volume, bucket, directory, missing path, and key entities.

## Important APIs and functions
`testNSSummaryBasicInfoRoot` seeds root prefix ACL/metadata and asserts root entity type, counts, ACL conversion, and metadata. Instance methods test volume counts and `VolumeObjectDBInfo`, bucket counts and `BucketObjectDBInfo` for supplied `BucketLayout`, directory counts/quota defaults, missing-path `PATH_NOT_FOUND`, and key-level `KeyObjectDBInfo` including replication type.

## Control flow, state, and persistence
Only the root test writes to the prefix table; all methods call `NSSummaryEndpoint.getBasicInfo(path)` and assert the response entity. Persistence is through the caller-provided `ReconOMMetadataManager` tables and namespace summary state prepared by concrete tests.

## Dependencies and integration points
It integrates `NSSummaryEndpoint`, `ReconOMMetadataManager`, OM prefix ACLs, `NamespaceSummaryResponse`, object DB info DTOs, bucket layouts, and response statuses. It is designed for reuse by FSO, OBS, legacy, and mixed-layout tests.

## Risks and edge cases
The expected counts are hard-coded to a specific fixture shape, so changes in concrete test data require synchronized updates. The root ACL setup assumes the root prefix table key and ACL conversion behavior. The class is not independently executable because most methods are helpers rather than annotated tests.

## Test signals
High-value shared assertions for endpoint response contracts across namespace layouts. It covers success and not-found paths but not authorization or malformed path handling.
