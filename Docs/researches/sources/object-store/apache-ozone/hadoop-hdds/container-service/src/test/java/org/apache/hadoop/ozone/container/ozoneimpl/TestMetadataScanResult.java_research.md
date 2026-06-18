## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestMetadataScanResult.java

Purpose: Unit tests for `MetadataScanResult`, covering healthy empty-error results, unhealthy error aggregation, and deleted-container representation.

Important APIs/types/functions: `MetadataScanResult.fromErrors`, `MetadataScanResult.deleted`, `ContainerTestUtils.getMetadataScanError`, and JUnit assertions.

Control flow: Each test constructs one result and asserts error flags, deletion flags, error-list size, and human-readable `toString` content. Two-error aggregation verifies plural count handling.

State and persistence behavior: Pure immutable-result testing; no filesystem or database state.

Dependencies and integration points: Supports scanner tests by validating the result objects that metadata scanners return to container controllers and on-demand/background scanners.

Risks and test signals: Good regression coverage for distinguishing deletion from corruption. It does not validate error ordering or specific `ContainerScanError` fields beyond count.
