# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/main/java/org/apache/hadoop/ozone/om/ScmClient.java

Purpose: `ScmClient` wraps OM's SCM block and container-location protocol clients and adds cache layers for container pipelines and datanode details. It reduces repeated SCM lookups while avoiding reuse of invalid empty or incomplete EC pipelines.

Important APIs and types: Constructor inputs are `ScmBlockLocationProtocol`, `StorageContainerLocationProtocol`, and `OzoneConfiguration`. Public methods include `getBlockClient`, `getContainerClient`, `getContainerLocations`, and `close`. Static helpers create the container location `LoadingCache`, create the datanode cache, and rebuild a pipeline using canonical cached `DatanodeDetails`.

Control flow: `getContainerLocations` optionally invalidates requested IDs, calls `containerLocationCache.getAll`, filters returned pipelines that are empty or EC pipelines missing any data replica index, invalidates those bad entries, and returns the result. Cache loading calls SCM single or batch APIs and normalizes datanode objects through `newPipelineWithDNCache`. Missing containers from `InvalidCacheLoadException` return only already cached present pipelines.

State and persistence behavior: State is transient Guava cache state plus metrics registered through `CacheMetrics`. No disk state is written. Cache expiry and size are controlled by OM config keys.

Dependencies and integration points: OM key lookup and block-location response paths use this wrapper to resolve container pipelines. It depends on SCM protocols, `Pipeline`, `DatanodeDetails`, replication configs, and Ozone cache metrics.

Risks and test signals: Returning invalid pipelines while also invalidating them means callers must tolerate the current result containing unusable entries. EC completeness checks only verify data indexes, not parity indexes. Tests should cover force refresh, batch load partial misses, datanode detail reuse after hostname/IP changes, empty pipeline invalidation, insufficient EC pipeline invalidation, and metrics unregister on close.
