# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/fs/ozone/TestSafeMode.java

Purpose: verifies O3FS and OFS implement Hadoop `SafeMode` against SCM safe mode state and force-exit behavior.

Important APIs/types/functions: `MiniOzoneClusterProvider` creates reusable clusters. `ofs` and `o3fs` call `testSafeMode` with URI builders. `testSafeMode` casts the filesystem to `SafeMode`, checks `GET`, stops datanodes, restarts SCM without waiting for normal exit, checks safe mode, calls `FORCE_EXIT`, and verifies SCM cannot allocate a writable container because datanodes remain down.

Control flow: each test creates a fresh cluster, volume, and bucket, opens either `ofs://om/` or `o3fs://bucket.volume.om/`, performs safe-mode state transitions, and closes the filesystem.

State and persistence behavior: safe mode reflects SCM runtime state rather than file metadata. Force exit changes SCM safe mode status, but container allocation still fails due to absent datanodes, proving the test did not restart capacity.

Dependencies and integration points: uses Hadoop `SafeMode` and `SafeModeAction`, `MiniOzoneClusterProvider`, `StorageContainerManager` writable container factory, `RatisReplicationConfig`, and O3FS/OFS URI schemes.

Risks: depends on cluster restart semantics and datanode shutdown behavior. Allocation failure is used as a secondary check that force exit does not imply datanode availability.

Test signals: catches missing SafeMode implementation on filesystem classes, incorrect propagation of SCM safe mode, and broken force-exit handling.
