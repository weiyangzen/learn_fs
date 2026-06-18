# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/ozone/test/FreonTests.java

Purpose: This abstract harness groups data-writing Freon generator tests so they can run against one shared non-HA mini cluster with smaller test-oriented client block/chunk settings.

Important APIs and types: It extends `ClusterForTests<MiniOzoneCluster>`, uses `ClientConfigForTesting`, `StorageUnit.MB`, and nested test classes from `org.apache.hadoop.ozone.freon`: `TestDNRPCLoadGenerator`, `TestHadoopDirTreeGenerator`, `TestHadoopNestedDirGenerator`, `TestHsyncGenerator`, `TestOmBucketReadWriteFileOps`, `TestOmBucketReadWriteKeyOps`, and `TestRandomKeyGenerator`.

Control flow: `createOzoneConfig` starts from the base cluster config and applies a 4 MB chunk size and 256 MB block size through `ClientConfigForTesting`. Each nested Freon test class overrides `cluster()` to return the shared cluster.

State and persistence behavior: Nested generator tests create substantial volumes, buckets, directories, keys, and hsync state in the mini cluster. The harness itself only alters client config and provides shared cluster access.

Dependencies and integration points: It connects Freon load/generator tests to the common cluster lifecycle. Grouping these tests separately from `NonHATests` keeps heavier data-writing tests out of the general non-HA suite.

Risks: Shared cluster state and heavier IO can make runtime and cleanup more expensive. Configuration values are tuned for tests, so performance or layout behavior may not match production defaults.

Test signals: Signals come from nested Freon tests: successful DN RPC load generation, Hadoop directory tree generation, nested directory creation, hsync generation, OM bucket read/write key and file operations, and random key generation.
