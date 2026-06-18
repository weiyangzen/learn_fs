# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/OMMetadataManagerTestUtils.java

## Purpose
This final test utility class builds OM and Recon OM metadata fixtures for Recon tests. It creates temporary OM DBs, copies OM checkpoints into Recon, writes key/directory/deleted-key records for multiple bucket layouts, provides mock OM service providers, and creates pipeline/block location helpers.

## Important APIs and functions
`initializeNewOmMetadataManager` creates an OM metadata manager with a default `sampleVol/bucketOne`; `initializeEmptyOmMetadataManager` creates an empty one. `getTestReconOmMetadataManager` checkpoints an OM DB, starts `ReconOmMetadataManagerImpl`, and imports the checkpoint. The overloaded `writeDataToOm`, `writeKeyToOm`, `writeOpenFileToOm`, `writeOpenKeyToOm`, `writeDeletedKeysToOm`, `writeDirToOm`, and `writeDeletedDirToOm` methods populate OM tables with legacy, default, and FSO key shapes. `getMockOzoneManagerServiceProvider` and `getMockOzoneManagerServiceProviderWithFSO` return Mockito-backed providers with table names. `getRandomPipeline` and `getOmKeyLocationInfo` create SCM block-location fixtures.

## Control flow, state, and persistence
The class writes directly to RocksDB-backed OM tables and creates DB checkpoints on disk. It maintains a static `OzoneConfiguration configuration` reused by `getTestReconOmMetadataManager`; callers can read or replace it through accessors. Key-building branches on `BucketLayout.FILE_SYSTEM_OPTIMIZED` to choose object-ID path keys versus regular ozone keys.

## Dependencies and integration points
It is used throughout Recon endpoint and task tests, including container, blocks, cluster state, namespace summary, and deleted-key scenarios. It integrates with OM helpers (`OmKeyInfo`, `OmBucketInfo`, `OmDirectoryInfo`, `RepeatedOmKeyInfo`), Recon recovery (`ReconOMMetadataManager`), SCM pipeline classes, and Mockito.

## Risks and edge cases
The static configuration can leak settings between tests unless reset. Many helpers have long parameter lists, so object ID and parent ID ordering mistakes can silently create invalid FSO paths. Several generated records omit optional fields such as ACLs, timestamps, or replication variants unless specifically supplied. Mock table names are important because downstream tasks branch on table names.

## Test signals
This file is a fixture provider rather than a test. Its correctness is exercised indirectly by endpoint tests in this subset, especially `TestContainerEndpoint`, `TestBlocksEndPoint`, and `TestClusterStateEndpoint`.
