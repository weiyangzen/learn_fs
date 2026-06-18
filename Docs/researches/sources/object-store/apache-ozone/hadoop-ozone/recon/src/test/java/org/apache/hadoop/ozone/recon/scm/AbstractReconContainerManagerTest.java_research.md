# sources/object-store/apache-ozone/hadoop-ozone/recon/src/test/java/org/apache/hadoop/ozone/recon/scm/AbstractReconContainerManagerTest.java

## Purpose
Shared test fixture for Recon SCM container-manager tests. It creates a real Recon SCM RocksDB store, real `ReconPipelineManager`, real `ReconContainerManager`, and a mocked `StorageContainerServiceProvider` with representative container responses.

## Important APIs, types, and functions
- Creates `ReconSCMDBDefinition` tables with `DBStoreBuilder`.
- Builds SCM HA stubs (`SCMHAManagerStub`, `SCMHADBTransactionBufferStub`) and `SequenceIdGenerator`.
- Creates `SCMNodeManager`, `ReconPipelineManager`, `ReconContainerManager`, `ContainerReplicaPendingOps`, and mocked `ContainerHealthSchemaManager`/`ReconContainerMetadataManager`.
- Helper methods expose `getConf`, `getPipelineManager`, `getContainerManager`, `getContainerTable`, and `getTestContainer` overloads.

## Control flow
`@BeforeEach` configures temp metadata paths, creates the DB store and transaction buffer, mocks max layout versions, initializes node and pipeline managers, and instantiates a container manager wired to a mocked SCM service provider. `@AfterEach` closes the pipeline manager and DB store. Helper methods create container-with-pipeline objects for open, closed, quasi-closed, and ranged container sets.

## State and persistence behavior
The fixture backs container and pipeline managers with real RocksDB tables. Container additions and state transitions performed by subclasses can be validated both through in-memory managers and DB table reads. The mocked SCM provider returns containers 100, 101, 102 and a batch range 200-299 across lifecycle states.

## Dependencies and integration points
It provides the integration base between Recon SCM DB definitions, container state management, pipeline state management, HA transaction buffering, node topology, and SCM service-provider RPC contracts.

## Risks and edge cases
Because this base creates real managers with mocked support services, subclasses may depend on the mocked provider's fixed IDs and states. It uses a null event publisher in some flows and mocked health/metadata managers, so tests extending it do not validate those side effects.

## Test signals
The fixture itself has no assertions, but subclasses use it to assert DB persistence, container existence, pipeline membership, lifecycle state transitions, replica history, and sync behavior.
