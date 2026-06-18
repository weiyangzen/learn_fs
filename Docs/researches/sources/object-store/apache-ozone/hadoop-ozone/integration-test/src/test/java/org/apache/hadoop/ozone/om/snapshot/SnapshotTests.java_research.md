# sources/object-store/apache-ozone/hadoop-ozone/integration-test/src/test/java/org/apache/hadoop/ozone/om/snapshot/SnapshotTests.java

## Purpose
Abstract nested-test aggregator for OM snapshot filesystem tests across bucket layouts and linked-bucket modes. It provides one shared mini-cluster and instantiates `TestOmSnapshotFileSystem` variants for FSO, FSO with linked buckets, legacy, and legacy with linked buckets.

## Important APIs and Types
The class `SnapshotTests` extends `ClusterForTests<MiniOzoneCluster>`. It overrides `onClusterReady` and defines nested classes `OmSnapshotFileSystemFso`, `OmSnapshotFileSystemFsoWithLinkedBuckets`, `OmSnapshotFileSystemLegacy`, and `OmSnapshotFileSystemLegacyWithLinkedBuckets`, each extending `TestOmSnapshotFileSystem`.

## Control Flow
When the cluster is ready, `onClusterReady` stops the OM key manager so deletion services do not purge keys that snapshot filesystem tests still need to read. Each nested class calls the superclass constructor with a bucket layout (`FILE_SYSTEM_OPTIMIZED` or `LEGACY`) and linked-bucket flag, and returns the shared cluster from `cluster()`.

## State and Persistence
The key state change is stopping the key manager/deletion services for the shared cluster. Snapshot filesystem tests then operate against persistent OM metadata without background deletion removing test data prematurely.

## Dependencies and Integration Points
This file integrates JUnit nested tests, the Ozone test cluster provider, bucket layout variants, linked bucket scenarios, and shared snapshot filesystem test logic in `TestOmSnapshotFileSystem`.

## Risks and Edge Cases
Stopping the key manager affects all nested tests and assumes those tests do not require active deletion services. Because the implementation is an aggregator, failures will often originate in the inherited `TestOmSnapshotFileSystem` behavior rather than this file.

## Test Signals
Signals are indirect: all nested snapshot filesystem variants run against the same cluster configuration and bucket-layout matrix while preserving readable deleted/snapshot key state.
