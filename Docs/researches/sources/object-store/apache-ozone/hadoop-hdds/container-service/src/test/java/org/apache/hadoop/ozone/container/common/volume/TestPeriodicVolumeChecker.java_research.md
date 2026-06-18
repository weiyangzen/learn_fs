# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestPeriodicVolumeChecker.java

## Purpose
Tests `StorageVolumeChecker.checkAllVolumeSets()` periodic scanning, min-gap skipping, and scan metrics across immutable, data, and metadata volume sets.

## Important APIs, Types, And Functions
Uses `StorageVolumeChecker.registerVolumeSet`, `checkAllVolumeSets`, `BackgroundVolumeScannerMetrics`, `FakeTimer`, `MutableVolumeSet`, and `TestStorageVolumeChecker.DummyChecker`.

## Control Flow
The test registers two immutable sets plus data and metadata mutable sets, advances fake time, runs a first scan, advances within the min gap and expects a skipped iteration, then advances by the periodic interval and expects a second scan.

## State And Persistence
Volume directories are temporary. Scan timestamps and metrics counters are in-memory state.

## Dependencies And Integration Points
Uses datanode disk-check configuration, metadata storage config, fake timer infrastructure, and `TestVolumeSet.assertNumVolumes`.

## Risks And Edge Cases
Depends on default gap/interval values and exact registered volume counts. Changes in metric classification can alter expected counts.

## Test Signals
Scan iteration, data scan, metadata scan, skipped iteration, last-scanned volume count, and volume health counts are asserted.
