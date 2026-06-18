# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/utils/TestHddsVolumeUtil.java

## Purpose
Validates `HddsVolumeUtil` Schema V3 DB-store loading and placement across data volumes and optional DB volumes, including restart and failure handling.

## Important APIs, Types, And Functions
Uses `HddsVolumeUtil.loadAllHddsVolumeDbStore`, static-mocked `initPerDiskDBStore`, `MutableVolumeSet`, `StorageVolumeUtil` typed filters, and `HddsVolume` DB health methods.

## Control Flow
Setup enables Schema V3 and creates three data and three DB volumes. Tests format/create working dirs, rebuild volume sets to simulate restart, load DB stores with or without DB volumes, and delete a DB volume VERSION file to validate duplicate DB-store prevention.

## State And Persistence
VERSION files, cluster working directories, DB parent directories, and storage-ID subdirectories are created under temp paths. Restart is simulated by shutdown and reconstruction.

## Dependencies And Integration Points
Uses Ozone data and DB directory configs, `ContainerTestUtils.enableSchemaV3`, `VolumeCheckResult`, and Mockito static mocking.

## Risks And Edge Cases
The bad DB-volume scenario depends on DB placement assigning at least one Hdds volume to the failed DB volume. Static mocking must not leak past the test scope.

## Test Signals
DB parent placement, dbVolume linkage, failed-volume counts, DB load flags, `VolumeCheckResult.FAILED`, and absence of duplicate local DB dirs validate behavior.
