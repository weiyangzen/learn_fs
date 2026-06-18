# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/dn/volume/TestDatanodeHddsVolumeFailureDetection.java

Purpose: Integration tests proving datanodes detect failed HDD volumes when chunk files, container metadata, or RocksDB directories are corrupted under both schema V3 and older schema modes.

Important APIs, types, and functions: Uses `MiniOzoneCluster`, `OzoneClient`, `ContainerOperationClient`, `DatanodeTestUtils`, `HddsVolume`, `MutableVolumeSet`, `DatanodeStoreCache`, `HddsVolume.checkDbHealth`, and `VolumeCheckResult`. Helpers are `newCluster`, `createKey`, and `readKeyToTriggerCheckVolumeAsync`.

Control flow: Each parameterized test builds a one-datanode cluster with replication one, container cache size one, zero min free space, failed volume tolerance one, and zero disk-check min gap. `corruptChunkFile` writes a key, locates chunk files under the volume cluster/current/container/chunks path, replaces chunk files with directories, makes the volume bad, reads the key to trigger async volume check, and waits for one failed volume. `corruptContainerFile` creates a standalone container, makes its metadata dir unwritable, makes the volume bad, attempts close and expects `IOException`, then waits for failed volume detection. `corruptDbFile` writes/closes a container, evicts it from cache by creating another container, replaces DB directory with a file, invalidates schema V3 cache if needed, triggers read failure, and waits for failed volume detection. `corruptDbFileWithoutDbHandleCacheInvalidation` directly exercises `HddsVolume.checkDbHealth` for schema V3, expecting first observed failure to still return healthy and subsequent failure to return failed.

State and persistence behavior: The tests create keys, containers, chunk files, container metadata, and RocksDB directories on real temp datanode volumes. Failure injection renames or permission-mutates those paths and later restores them. Volume failure state is stored in `MutableVolumeSet` failed volume lists and DB health failure counters.

Dependencies and integration points: Integrates client read path, container close path, volume health checks, datanode store cache, schema-specific DB locations, SCM container creation, and helper failure injection.

Risks: Filesystem permission and rename semantics can vary by OS and user. RocksDB cache behavior is schema-dependent and must be explicitly invalidated for some tests. Tests rely on cleanup restoration in `finally` blocks to avoid poisoning cluster shutdown.

Test signals: Expected client read or close operations throw `IOException`; `waitForHandleFailedVolume` observes exactly one failed volume; direct DB health returns `HEALTHY` then `FAILED` in the no-cache-invalidation scenario.
