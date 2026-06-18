# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestHddsVolume.java

## Purpose
Broad unit coverage for `HddsVolume`: VERSION metadata, formatting, tmp cleanup, reserved-space accounting, Schema V3 DB placement, DB cache cleanup, health metrics, container paths, usage metrics, and directory permissions.

## Important APIs, Types, And Functions
Exercises `HddsVolume.Builder`, `format`, `createWorkingDir`, `createTmpDirs`, `shutdown`, `failVolume`, `check`, `DatanodeVersionFile`, `StorageVolumeUtil`, `VolumeUsage`, `DatanodeStoreCache`, and `VolumeInfoMetrics`.

## Control Flow
Tests format and compare VERSION fields, create tmp/delete/disk-check dirs and clear leftovers, save usage on shutdown, run conservative available-space formulas, create DB stores with and without DB volumes, fail volumes to clear cache, delete DB dirs to force health failure, and check POSIX permissions.

## State And Persistence
Real temp filesystem state includes VERSION files, cluster dirs, tmp dirs, deleted-container dirs, disk-check dirs, DB dirs, persisted used-space cache, and POSIX permissions. Metrics and committed bytes are in-memory state.

## Dependencies And Integration Points
Uses Ozone config keys for reserved space, min free space, DB dirs, data-dir permissions, Schema V3 helpers, Hadoop metrics, Commons IO, and mock space usage factories.

## Risks And Edge Cases
Permission tests need POSIX support. Singleton DB cache and static config require cleanup. Space-accounting assertions encode exact reserved-capacity formulas.

## Test Signals
VERSION equality, directory existence/removal, persisted used-space value, computed capacity/available values, DB parent paths, cache size, `VolumeCheckResult`, metrics gauges, and POSIX permission equality validate behavior.
