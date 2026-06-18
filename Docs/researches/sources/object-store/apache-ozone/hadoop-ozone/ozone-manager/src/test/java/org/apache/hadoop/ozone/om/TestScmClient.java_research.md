# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/TestScmClient.java

Purpose: Tests `ScmClient` container-location and datanode-details caching behavior.

Important APIs and types: `ScmClient`, `StorageContainerLocationProtocol.getContainerWithPipelineBatch`, `ScmBlockLocationProtocol`, Guava `Cache<DatanodeID,DatanodeDetails>`, `ContainerWithPipeline`, `ContainerInfo`, `Pipeline`, `DatanodeDetails`, and `DatanodeID`.

Control flow: setup constructs `ScmClient` with mocked SCM protocols. Parameterized tests prepopulate cache with one SCM batch call, then request different ID sets with or without force refresh and verify only expected container IDs are fetched. Failure tests make SCM throw checked and unchecked exceptions. Datanode cache tests check stats and IP-address updates replacing cached node details.

State and persistence: all state is in-memory cache state inside `ScmClient` and Guava datanode detail caches. No filesystem or RocksDB use.

Dependencies and integration points: used by key lookup/list APIs to attach live pipelines to OM block locations while avoiding repeated SCM calls. Datanode detail cache preserves object identity unless updated node data arrives.

Risks and edge cases: force refresh must bypass cache for requested IDs; unchecked SCM errors are wrapped, while IOExceptions propagate; datanode IP changes must update cached node objects so stale addresses do not persist in refreshed pipelines.

Test signals: exact SCM batch call sets and counts, returned pipelines equal expected container pipelines, exception identity/cause assertions, cache miss stat count, and `assertSame`/IP checks for datanode replacement.
