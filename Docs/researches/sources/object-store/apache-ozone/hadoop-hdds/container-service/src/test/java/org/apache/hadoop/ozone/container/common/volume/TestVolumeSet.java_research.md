# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestVolumeSet.java

## Purpose
Tests `MutableVolumeSet` initialization, explicit volume failure, inconsistent volume detection, shutdown behavior, startup failure metrics, and interruption preservation.

## Important APIs, Types, And Functions
Uses `MutableVolumeSet` constructors, `getVolumesList`, `getFailedVolumesList`, `getVolumeMap`, `failVolume`, `shutdown`, helper `assertNumVolumes`, and `HddsVolumeUtil.getHddsRoot`.

## Control Flow
Setup configures two data and metadata dirs. Tests load both volumes, fail one, add a non-empty missing-VERSION volume and reload, shutdown and still read usage, detect a read-only startup failure, and reflectively invoke `checkAllVolumes` while interrupted.

## State And Persistence
Temporary volume directories, failed lists, volume maps, and metrics gauges are mutated and cleaned up.

## Dependencies And Integration Points
Uses Ozone data/metadata directory configs, Commons IO cleanup, metrics assertions, and read-only filesystem assumptions.

## Risks And Edge Cases
Read-only behavior is platform-dependent. The interruption test manipulates current-thread interrupt state.

## Test Signals
Volume counts, failed counts, volume map membership, and metrics gauges validate behavior.
