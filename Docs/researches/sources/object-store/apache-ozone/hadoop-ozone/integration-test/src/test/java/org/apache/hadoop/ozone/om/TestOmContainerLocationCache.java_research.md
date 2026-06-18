# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/TestOmContainerLocationCache.java

## Purpose
Integration test for OM-side container location caching during key reads. It builds an `OzoneManager` with mocked SCM block/container protocols and mocked datanode `XceiverClientGrpc` instances so client reads can exercise cached container pipelines without a full datanode cluster.

## Important APIs, types, and functions
- Uses `OmTestManagers`, `ObjectStore`, `RpcClient`, `OzoneBucket`, `OzoneKeyDetails`, and `OzoneOutputStream` as the client/OM surface.
- Mocks `ScmBlockLocationProtocol.allocateBlock`, `StorageContainerLocationProtocol.getContainerWithPipelineBatch`, and datanode `sendCommandAsync` for `WriteChunk`, `PutBlock`, `GetBlock`, and `ReadChunk`.
- Helper methods create Ratis and EC `Pipeline` instances, SCM `AllocatedBlock` objects, `ContainerWithPipeline` responses, block/chunk protobuf responses, and Mockito matchers for pipelines and command types.
- Parameter sources divide errors into refresh-triggering failures (`CLOSED_CONTAINER_IO`, `CONTAINER_NOT_FOUND`, gRPC `UNAVAILABLE`) and non-refresh failures (`UNAUTHENTICATED`, arbitrary `IOException`).

## Control flow
`setUp` configures topology-aware reads, initializes OM metadata, creates a test volume plus regular and versioned buckets, and replaces the RPC client's xceiver factory with mocks. Each test increments the container id and resets SCM/datanode mocks. Happy-path reads write a key, fetch its container pipeline from SCM once, read from the mocked datanode, then read a second key in the same container and assert SCM is not called again. Error-path tests inject datanode `GetBlock` or `ReadChunk` failures, optionally reconfigure SCM to return a DN2 pipeline, and assert either a successful refresh/retry or a fast propagated exception.

## State and persistence behavior
Persistent OM state is limited to in-process metadata tables created through `OMRequestTestUtils`; actual block data is synthetic datanode responses. The relevant persisted signal is that key metadata stores a block location whose container id is later resolved through OM's container location cache. The cache should retain usable Ratis pipelines, refuse to retain empty pipelines, and cache EC pipelines only when all required data replica indexes are present.

## Dependencies and integration points
This test sits at the boundary between OM metadata, SCM container-location lookup, and the Ozone RPC client read path. It depends heavily on Mockito spies, `XceiverClientManager`, HDDS pipeline/container helper classes, protobuf datanode command types, checksum creation, and Ozone client stream semantics. It also integrates with network-topology-aware read configuration.

## Risks and edge cases
The main risks are stale cached container locations after datanode movement, caching unusable empty pipelines, EC reads with insufficient data indexes, and over-refreshing on authentication or unrelated IO failures. Mockito matching is narrow: changes to acquisition methods, EC pipeline shape, or datanode command sequencing may make this test fail before product behavior is actually broken.

## Test signals
Assertions check byte-for-byte data reads, exact SCM `getContainerWithPipelineBatch` call counts, expected exception classes/messages, and EC cache/no-cache behavior across repeated `getKey` calls. These signals directly verify cache reuse, cache invalidation, and non-cacheable pipeline handling.
