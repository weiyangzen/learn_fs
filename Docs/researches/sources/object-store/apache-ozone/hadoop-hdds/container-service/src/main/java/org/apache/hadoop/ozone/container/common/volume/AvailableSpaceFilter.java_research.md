<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/AvailableSpaceFilter.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/AvailableSpaceFilter.java

## Purpose

`AvailableSpaceFilter` selects `HddsVolume`s that have enough hard-min-free available space to create a new container and records rejected volumes for diagnostics. The complete 84-line file was read.

## Important APIs, Types, and Functions

The class implements `Predicate<HddsVolume>`. Constructor input is `requiredSpace`. Main methods are `test(HddsVolume)`, package-private `foundFullVolumes()`, `mostAvailableSpace()`, and `toString()`.

## Control Flow

`test` reads a volume's `StorageLocationReport`, computes hard-limit available space as remaining minus committed minus `vol.getFreeSpaceToSpare(capacity)`, compares it to `requiredSpace`, updates per-volume metrics, tracks the maximum available amount seen, adds rejected reports to `fullVolumes`, and returns eligibility. If the volume is above the hard limit but inside the softer reported spare band, it increments a soft-band metric.

## State and Persistence Behavior

The filter stores `fullVolumes` and `mostAvailableSpace` for the scan instance. It persists nothing. Metrics side effects occur on `VolumeInfoMetrics` if present.

## Dependencies and Integration Points

It depends on `HddsVolume`, `StorageLocationReport`, and volume info metrics. It is used by volume/container placement code when selecting space for a new container.

## Risks and Edge Cases

The comparison is strict `available > requiredSpace`; exactly equal space is rejected. The filter is stateful and not thread-safe; reuse across independent scans can mix diagnostics. Negative committed/remaining anomalies can produce misleading availability.

## Test Signals

Tests should cover hard-limit rejection, exact-equality rejection, soft-band metric increments, full-volume list/toString, most-available tracking, null metrics handling, and state reset by using new filter instances.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/volume/AvailableSpaceFilter.java -->
