<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/BackgroundVolumeScannerMetrics.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/BackgroundVolumeScannerMetrics.java

## Purpose

`BackgroundVolumeScannerMetrics` registers Hadoop metrics for background volume scanning: volumes scanned in the last iteration, scan iteration count, data/metadata volume scans, and skipped iterations. The complete 119-line file was read.

## Important APIs, Types, and Functions

The class is annotated with `@Metrics` and created via `create()`. It exposes getters and mutators for `numVolumesScannedInLastIteration`, `numScanIterations`, `numDataVolumeScans`, `numMetadataVolumeScans`, and `numIterationsSkipped`, plus `unregister()`.

## Control Flow

`create` registers a metrics source named after the class. Scanner code sets the last-iteration gauge, increments scan iteration count, increments data and metadata scan counters by count, and increments skipped iterations when minimum scan gap prevents work. `unregister` removes the source from the default metrics system.

## State and Persistence Behavior

All state is in-memory metrics. No persistent data is written.

## Dependencies and Integration Points

It depends on Hadoop metrics2 annotations, `DefaultMetricsSystem`, `MutableGaugeLong`, and `MutableCounterLong`, and integrates with background volume scanner code.

## Risks and Edge Cases

The metrics source name is fixed, so only one scanner metrics instance can be registered cleanly per metrics system unless previous instances unregister. Counter increments accept caller-supplied counts without validation.

## Test Signals

Tests should verify registration/unregistration, gauge set/get, each counter increment, skipped iteration count, and lifecycle behavior across repeated create calls.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/BackgroundVolumeScannerMetrics.java -->
