# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/test/java/org/apache/hadoop/ozone/container/common/volume/TestStorageVolumeHealthChecks.java

## Purpose
Tests real `StorageVolume` health checks for Hdds, metadata, and DB volumes using injectable disk checks, including existence, permissions, IO and timeout sliding windows, and directory selection.

## Important APIs, Types, And Functions
Uses `StorageVolume.check`, `DiskCheckUtil.setTestImpl`, `DatanodeConfiguration`, `StorageVolume.recordTimeoutAndCheckFailure`, timeout sliding windows, and builders for `HddsVolume`, `MetadataVolume`, and `DbVolume`.

## Control Flow
Setup resets disk-check injection, configures tolerances, and resets a test clock. Tests inject failing existence/permission checks, simulate full-volume IO skip, disable IO checks, validate tolerance defaults, run IO result sequences through time windows, verify checked directories, and test timeout tolerance/expiry/disable behavior.

## State And Persistence
Temporary storage dirs, tmp dirs, disk-check dirs, volume usage counters, sliding-window event queues, and simulated time are the meaningful state.

## Dependencies And Integration Points
Integrates volume builders, `DiskCheckUtil`, `TestClock`, datanode health config, and all three storage volume subclasses.

## Risks And Edge Cases
The static temp path is manually cleaned before each test. Sliding-window tests rely on exact simulated time and tolerance semantics. Disk-check override state must be reset.

## Test Signals
`VolumeCheckResult` values, event counts, asserted disk-check paths, and config-derived tolerance values validate behavior.
