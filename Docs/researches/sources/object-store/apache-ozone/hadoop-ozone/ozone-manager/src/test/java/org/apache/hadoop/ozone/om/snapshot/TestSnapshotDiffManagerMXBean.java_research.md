# sources/object-store/apache-ozone/hadoop-ozone/ozone-manager/src/test/java/org/apache/hadoop/ozone/om/snapshot/TestSnapshotDiffManagerMXBean.java

## Purpose
`TestSnapshotDiffManagerMXBean` verifies that `SnapshotDiffManager` registers its JMX MXBean and exposes persisted snapshot diff jobs through the `SnapshotDiffJobs` attribute.

## Important APIs, Types, and Functions
- `SnapshotDiffManager` constructor registers the MBean.
- Platform `MBeanServer` and `ObjectName("Hadoop:service=OzoneManager,name=SnapshotDiffManager")` are used for lookup.
- `CompositeData[]` represents JMX job rows.
- `RocksDbPersistentMap<String, SnapshotDiffJob>` writes test job state directly to the job table.

## Control Flow
Setup opens a temporary RocksDB database with job/report/purged job column families, builds a codec registry for `SnapshotDiffJob`, mocks enough `OzoneManager` and metadata manager state for construction, and creates `SnapshotDiffManager`. The test asserts that the MBean is registered, reads an initially empty `SnapshotDiffJobs` attribute, writes a queued job directly to the job table, reads the attribute again, and checks job id, from/to snapshot names, and sub-status.

## State and Persistence Behavior
The JMX view is backed by the persisted snapshot diff job table. Adding a job to RocksDB changes the MXBean attribute output without needing a separate in-memory registration step.

## Dependencies and Integration Points
This test integrates JMX registration, RocksDB-backed persistent maps, Ozone manager metadata configuration, and snapshot diff job codecs.

## Risks and Edge Cases
- Global MBean registration can be sensitive to prior tests if teardown does not unregister correctly.
- The test verifies a small subset of exposed composite fields, not every MXBean field.

## Test Signals
Passing means operators can discover `SnapshotDiffManager` through JMX and inspect persisted diff jobs.
