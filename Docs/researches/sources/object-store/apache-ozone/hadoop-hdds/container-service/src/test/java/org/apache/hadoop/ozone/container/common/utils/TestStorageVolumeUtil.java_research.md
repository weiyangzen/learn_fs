# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/TestStorageVolumeUtil.java

## Purpose
Tests that `StorageVolumeUtil.checkVolume` does not create duplicate DB stores when checking an already initialized Hdds volume with DB volumes.

## Important APIs, Types, And Functions
Exercises `StorageVolumeUtil.checkVolume`, observes `HddsVolume.createDbStore` through a spy, and uses real `HddsVolume` and `DbVolume` builders.

## Control Flow
The test enables Schema V3, builds a DB volume and spied Hdds volume, checks the DB volume first, checks the Hdds volume twice, and verifies DB-store creation only on the first Hdds check.

## State And Persistence
Temporary VERSION files and DB-store directories are created. The existing DB-store directory is the state that prevents duplicate creation.

## Dependencies And Integration Points
Uses `MockSpaceUsageCheckFactory.NONE`, a mocked DB `MutableVolumeSet`, Schema V3 setup, and optional logging.

## Risks And Edge Cases
This is a focused invocation-count regression test and does not cover all failed DB-volume layouts.

## Test Signals
Both checks return true and `createDbStore` is verified exactly once.
