<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/HddsVolumeUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/HddsVolumeUtil.java

## Purpose

`HddsVolumeUtil` contains HDDS data-volume helpers for resolving the `hdds` root, initializing schema-v3 per-disk DB stores, loading DB stores for all HDDS volumes, and mapping dedicated DB volumes to data volumes. The complete 142-line file was read.

## Important APIs, Types, and Functions

Public APIs are `getHddsRoot(String)`, `initPerDiskDBStore(String, ConfigurationSource, boolean)`, and `loadAllHddsVolumeDbStore(MutableVolumeSet, MutableVolumeSet, boolean, Logger)`. Private helpers are `loadVolume` and `mapDbVolumesToDataVolumesIfNeeded`.

## Control Flow

`getHddsRoot` appends `HddsVolume.HDDS_VOLUME_DIR` unless the path already ends in it. `initPerDiskDBStore` opens or formats an uncached schema-v3 store and registers it through `BlockUtils.addDB`. `loadAllHddsVolumeDbStore` first maps DB volumes to data volumes using storage IDs, then runs `volume.loadDbStore(readOnly)` asynchronously for each HDDS volume and waits for all futures. Failures call `StorageVolumeUtil.onFailure` and log the failed volume.

## State and Persistence Behavior

The utility can create/open per-disk RocksDB stores and update `HddsVolume` objects with their associated `DbVolume`. It does not store state of its own. Persistent DB initialization is delegated to `BlockUtils` and volume implementations.

## Dependencies and Integration Points

It depends on `HddsVolume`, `DbVolume`, `MutableVolumeSet`, `BlockUtils`, `DatanodeStore`, `OzoneConsts.SCHEMA_V3`, and `StorageVolumeUtil` conversion/failure helpers.

## Risks and Edge Cases

`getHddsRoot` uses a suffix check rather than path-segment comparison, so unusual paths ending in the same string are accepted. Asynchronous load uses the common ForkJoin pool via `CompletableFuture.runAsync`, so large volume counts share global executor resources. `join` propagates unchecked exceptions if `loadVolume` ever throws beyond its catch block.

## Test Signals

Tests should cover root resolution, schema-v3 DB initialization in read-only and read-write modes, DB-volume-to-HDDS-volume mapping by storage ID, failed load invoking volume failure handling, and logging/timing with multiple volumes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/common/utils/HddsVolumeUtil.java -->
