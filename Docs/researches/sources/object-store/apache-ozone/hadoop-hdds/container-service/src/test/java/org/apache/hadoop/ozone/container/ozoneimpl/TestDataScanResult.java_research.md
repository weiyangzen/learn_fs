## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/ozoneimpl/TestDataScanResult.java

Purpose: Unit tests for `DataScanResult`, validating healthy, unhealthy metadata, direct data-error, and deleted-container result shapes.

Important APIs/types/functions: `DataScanResult.fromErrors`, `DataScanResult.unhealthyMetadata`, `DataScanResult.deleted`, `MetadataScanResult.fromErrors`, `ContainerMerkleTreeWriter`, and `ContainerMerkleTreeTestUtils.buildTestTree`.

Control flow: Tests build results from empty, singleton, and repeated errors. Assertions cover `hasErrors`, `isDeleted`, `getErrors`, `toString`, and merkle tree ownership/content. Metadata failure and deletion paths must produce an empty merkle tree, while data-error construction preserves the provided tree instance.

State and persistence behavior: Pure in-memory value-object testing; no persistent state. Static `TREE` is reused across tests.

Dependencies and integration points: Uses Ozone scan error factories and checksum merkle tree utilities. This connects scanner result modeling to checksum persistence expectations without invoking scanners.

Risks and test signals: The tests catch regressions where deleted or metadata-failed scans accidentally carry stale checksum trees, and where `toString` loses operator-facing error counts.
