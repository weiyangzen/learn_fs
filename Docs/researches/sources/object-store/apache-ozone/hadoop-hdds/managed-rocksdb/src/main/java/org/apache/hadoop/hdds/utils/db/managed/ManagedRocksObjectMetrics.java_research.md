<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksObjectMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksObjectMetrics.java

## Purpose

Registers Hadoop metrics counters for total managed RocksDB objects and leaked managed objects.

## Important APIs, types, and functions

Package: `org.apache.hadoop.hdds.utils.db.managed`. Main type: `ManagedRocksObjectMetrics`. Notable methods: `assertNoLeaks`, `create`. Key imports include `com.google.common.annotations.VisibleForTesting`, `org.apache.hadoop.hdds.annotation.InterfaceAudience`, `org.apache.hadoop.metrics2.annotation.Metric`, `org.apache.hadoop.metrics2.annotation.Metrics`, `org.apache.hadoop.metrics2.lib.DefaultMetricsSystem`, `org.apache.hadoop.metrics2.lib.MutableCounterLong`, `org.apache.hadoop.ozone.OzoneConsts`.

## Control flow

A singleton registers with DefaultMetricsSystem. ManagedRocksObjectUtils increments counters and tests can call assertNoLeaks.

## State and persistence behavior

Maintains mutable metrics counters in the process-wide metrics system.

## Dependencies and integration points

This type integrates with RocksDB JNI, Ozone HDDS utility classes, Hadoop metrics or test utilities where imported, and call sites in the HDDS DB layer. Native-facing classes also integrate with `hdds-rocks-native` JNI code and Maven native packaging.

## Risks and edge cases

Global singleton state can leak between tests; counter-only metrics cannot identify which object leaked without log stack traces.

## Test signals

Assert counter increments for tracked objects and leak reporting, with metrics-system isolation in repeated test runs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/managed-rocksdb/src/main/java/org/apache/hadoop/hdds/utils/db/managed/ManagedRocksObjectMetrics.java -->
