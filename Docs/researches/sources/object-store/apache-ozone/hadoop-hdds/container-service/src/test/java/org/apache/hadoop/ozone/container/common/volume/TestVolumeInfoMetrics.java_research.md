# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeInfoMetrics.java

## Purpose
Tests that `VolumeInfoMetrics` exposes Ozone-adjusted capacity gauges, raw filesystem gauges, min free space, and derived non-Ozone usage.

## Important APIs, Types, And Functions
Uses `VolumeInfoMetrics.getMetrics`, mocked `HddsVolume`, mocked `VolumeUsage`, `SpaceUsageSource.Fixed`, and a helper that extracts metric values by name.

## Control Flow
The test mocks volume metadata, reserved bytes, raw filesystem usage, and adjusted Ozone usage, collects metrics, checks expected gauges, and unregisters metrics in a finally block.

## State And Persistence
Only in-memory mocked metrics data is used. Metrics source registration is cleaned up.

## Dependencies And Integration Points
Connects Hdds metadata, `VolumeUsage`, Hadoop metrics collector internals, and min-free-space reporting.

## Risks And Edge Cases
Depends on exact metric names and formulas. Does not cover failed-volume or real filesystem metrics.

## Test Signals
Gauge equality for Ozone, filesystem, min-free, and non-Ozone metrics validates output.
